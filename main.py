import argparse
from sitemap_builder import SitemapBuilder
from database import Database
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import os


def draw_sitemap(structure):
    visited = set()
    nodes = {}
    edges = []

    def traverse(url):
        if url in visited:
            return

        visited.add(url)
        links = structure[url]

        if url not in nodes:
            nodes[url] = len(links)

        for link in links:
            edges.append((url, link))
            traverse(link)

    for url in structure:
        traverse(url)

    plt.figure(figsize=(12, 8))
    pos = {}
    node_sizes = []

    for i, (node, size) in enumerate(nodes.items()):
        pos[node] = (i % 10, i // 10)
        node_sizes.append(size)

    for node1, node2 in edges:
        plt.plot([pos[node1][0], pos[node2][0]], [pos[node1][1], pos[node2][1]], 'gray', linewidth=0.5)

    plt.scatter([pos[node][0] for node in nodes], [pos[node][1] for node in nodes], s=[size * 100 for size in node_sizes],
                c='lightblue', alpha=0.8, edgecolors='black', linewidths=0.5)

    plt.axis('off')
    plt.tight_layout()
    plt.savefig('sitemap.png')


def save_sitemap_xml(structure):
    root = ET.Element('urlset', xmlns='http://www.sitemaps.org/schemas/sitemap/0.9')

    for url, links in structure.items():
        url_element = ET.SubElement(root, 'url')
        loc_element = ET.SubElement(url_element, 'loc')
        loc_element.text = url

        for link in links:
            link_element = ET.SubElement(url_element, 'link')
            link_element.text = link

    tree = ET.ElementTree(root)
    tree.write('sitemap.xml', encoding='utf-8', xml_declaration=True)


def main():
    parser = argparse.ArgumentParser(description='Website Sitemap Builder')
    parser.add_argument('url', type=str, help='URL of the website')
    parser.add_argument('db_file', type=str, help='SQLite database file name')
    parser.add_argument('--max_depth', default=2, type=int, help='Maximum depth for the sitemap crawler')
    args = parser.parse_args()

    output_dir = args.url.rstrip('/').replace('http://', '').replace('https://', '')
    os.makedirs(output_dir, exist_ok=True)

    sitemap_builder = SitemapBuilder(args.url, max_depth=args.max_depth)
    time_consumed, links_found, structure = sitemap_builder.build_sitemap()

    xml_file = os.path.join(output_dir, 'sitemap.xml')
    draw_sitemap(structure)
    save_sitemap_xml(structure)

    os.rename('sitemap.xml', xml_file)
    os.rename('sitemap.png', os.path.join(output_dir, 'sitemap.png'))

    db_file = os.path.join(output_dir, args.db_file)
    db = Database(db_file)
    db.create_table()
    db.insert_record(args.url, time_consumed, links_found, xml_file)
    db.close()
    os.rename(args.db_file, db_file)


if __name__ == '__main__':
    main()
