# -*- coding: utf-8 -*-
"""Actualiza data.json con los precios semanales.
Fuentes: elrural.com (terneros zona centro + indice novillo arrendamiento)
y mercadoagroganadero.com.ar (respaldo del indice arrendamiento)."""
import re, json, sys, datetime
from bs4 import BeautifulSoup

URLS = {
    'terneros_live': 'https://www.elrural.com/mercados/ganadero/invernada-y-cria/invernada-y-cria-zona-centro/zona-centro-terneros-kg/',
    'terneros_idx':  'https://www.elrural.com/historicos/ganadero/zona-centro-terneros-kg/',
    'novillo_live':  'https://www.elrural.com/mercados/ganadero/precios-indicativos/indice-novillo-arrendamiento-precios-indicativos/',
    'novillo_idx':   'https://www.elrural.com/historicos/ganadero/indice-novillo-arrendamiento-precios-indicativos/',
    'mag':           'https://www.mercadoagroganadero.com.ar/dll/inicio.dll',
}
HEADERS = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36',
           'Accept-Language': 'es-AR,es;q=0.9'}
CAT_RE = re.compile(r'^(Terneros|Novillitos|Macho|Terneras|Hembras)', re.I)

def get(url):
    """Devuelve el HTML o None. Prueba requests y despues cloudscraper."""
    import requests
    try:
        r = requests.get(url, headers=HEADERS, timeout=30)
        if r.ok and len(r.text) > 2000 and 'Just a moment' not in r.text:
            return r.text
    except Exception:
        pass
    try:
        import cloudscraper
        s = cloudscraper.create_scraper()
        r = s.get(url, timeout=45)
        if r.ok and len(r.text) > 2000 and 'Just a moment' not in r.text:
            return r.text
    except Exception:
        pass
    print('AVISO: no se pudo descargar', url)
    return None

def dmy(s):
    m = re.match(r'^(\d{1,2})[-/](\d{1,2})[-/](\d{2,4})$', s.strip())
    if not m:
        return None
    d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
    if y < 100:
        y += 2000
    return '%04d-%02d-%02d' % (y, mo, d)

def num(v):
    v = re.sub(r'[^\d.,]', '', str(v)).replace('.', '').replace(',', '.')
    try:
        return float(v)
    except ValueError:
        return None

def parse_terneros(html):
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ')
    wm = re.search(r'Semana del\s+([\d-]{8,10})\s+al\s+([\d-]{8,10})', text, re.I)
    if not wm:
        return None
    end = dmy(wm.group(2))
    rows = {}
    for tr in soup.find_all('tr'):
        cells = [td.get_text(' ', strip=True) for td in tr.find_all(['td', 'th'])]
        if len(cells) >= 6 and CAT_RE.match(cells[0]):
            name = re.sub(r'\s+', ' ', cells[0])
            rows[name] = {'min': num(cells[3]), 'max': num(cells[4]), 'prom': num(cells[5])}
    if end and rows:
        return end, {'week': wm.group(1) + ' al ' + wm.group(2), 'rows': rows}
    return None

def parse_novillo(html):
    soup = BeautifulSoup(html, 'html.parser')
    wm = re.search(r'Semana\s+del\s+([\d/]{6,10})\s+al\s+([\d/]{6,10})', soup.get_text(' '), re.I)
    if not wm:
        return None
    end = dmy(wm.group(2))
    value = None
    for tb in soup.find_all('table'):
        t = tb.get_text(' ')
        if re.search(r'novillo\s+arrendamiento', t, re.I):
            vm = re.search(r'\$?\s*([\d.]+,\d+)', t)
            if vm:
                value = num(vm.group(1))
                break
    if end and value:
        return end, {'week': wm.group(1) + ' al ' + wm.group(2), 'value': value}
    return None

def index_links(html, title_re, limit=8):
    """Links de los posts mas recientes del archivo historico."""
    soup = BeautifulSoup(html, 'html.parser')
    out = []
    for a in soup.find_all('a', href=True):
        t = a.get_text(' ', strip=True)
        if '/mercado/' in a['href'] and re.search(r'\d{1,2} de \w+ de \d{4}\s*$', t) and re.match(title_re, t, re.I):
            if a['href'] not in out:
                out.append(a['href'])
    return out[:limit]

def parse_mag(html):
    """Indice Arrendamiento del sitio del MAG (respaldo)."""
    soup = BeautifulSoup(html, 'html.parser')
    text = soup.get_text(' ')
    vm = re.search(r'ndice\s+Arrend\.?\s*\$?\s*([\d.]+,\d+)', text, re.I)
    dm = re.search(r'(\d{2}/\d{2}/\d{4})', text)
    if vm and dm:
        end = dmy(dm.group(1))
        v = num(vm.group(1))
        if end and v:
            return end, {'week': 'MAG al ' + dm.group(1), 'value': v}
    return None

def main():
    with open('data.json', encoding='utf-8') as f:
        data = json.load(f)
    before = json.dumps(data, sort_keys=True)

    # --- Terneros: pagina en vivo + ultimos posts del historico ---
    html = get(URLS['terneros_live'])
    if html:
        r = parse_terneros(html)
        if r:
            data['terneros'][r[0]] = r[1]
    html = get(URLS['terneros_idx'])
    if html:
        for url in index_links(html, r'Zona Centro'):
            page = get(url)
            if page:
                r = parse_terneros(page)
                if r:
                    data['terneros'][r[0]] = r[1]

    # --- Novillo arrendamiento: elrural, con respaldo del MAG ---
    got_novillo = False
    html = get(URLS['novillo_live'])
    if html:
        r = parse_novillo(html)
        if r:
            data['novillo'][r[0]] = r[1]
            got_novillo = True
    html = get(URLS['novillo_idx'])
    if html:
        for url in index_links(html, r'Novillo Arren'):
            page = get(url)
            if page:
                r = parse_novillo(page)
                if r:
                    data['novillo'][r[0]] = r[1]
                    got_novillo = True
    if not got_novillo:
        html = get(URLS['mag'])
        if html:
            r = parse_mag(html)
            if r and r[0] not in data['novillo']:
                data['novillo'][r[0]] = r[1]

    data['terneros'] = dict(sorted(data['terneros'].items()))
    data['novillo'] = dict(sorted(data['novillo'].items()))
    data['updated'] = datetime.date.today().isoformat()

    if json.dumps(data, sort_keys=True) != before:
        with open('data.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
        print('data.json actualizado:', len(data['terneros']), 'semanas terneros,', len(data['novillo']), 'semanas novillo')
    else:
        print('Sin cambios')

if __name__ == '__main__':
    main()
