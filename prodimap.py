#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import json
import math
import os
import re
import sys
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Set

try:
    from openai import OpenAI
except Exception:
    OpenAI = None

# Data Prodi
PRODI_MAP = {
    1: "S1 PARIWISATA",
    2: "S1 MANAJEMEN",
    3: "S1 EKONOMI PEMBANGUNAN",
    4: "S1 AKUNTANSI",
    5: "D4 AKUNTASI PERPAJAKAN",
    6: "D3 AKUNTANSI",
    7: "S2 PENDIDIKAN BAHASA INGGRIS",
    8: "S2 PENDIDIKAN BAHASA INDONESIA",
    9: "S1 PENDIDIKAN MATEMATIKA",
    10: "S1 PENDIDIKAN ILMU PENGETAHUAN ALAM",
    11: "S1 PENDIDIKAN BIOLOGI",
    12: "S1 PENDIDIKAN BAHASA INGGRIS",
    13: "S1 PENDIDIKAN BAHASA DAN SASTRA INDONESIA",
    14: "PENDIDIKAN PROFESI GURU",
    15: "S2 ADMINISTRASI PUBLIK",
    16: "S1 ILMU KOMUNIKASI",
    17: "S1 ILMU ADMINISTRASI NEGARA",
    18: "S1 HUKUM",
    19: "S1 TEKNOLOGI PANGAN",
    20: "S1 PETERNAKAN",
    21: "S1 GIZI",
    22: "S1 AKUAKULTUR",
    23: "S1 AGROTEKNOLOGI",
    24: "S1 AGRIBISNIS",
    25: "D3 FARMASI",
    26: "S1 TEKNOLOGI INFORMASI",
    27: "S1 TEKNIK SIPIL",
    28: "S1 TEKNIK MESIN",
    29: "S1 TEKNIK MEKATRONIKA",
    30: "S1 TEKNIK INDUSTRI",
    31: "S1 TEKNIK ELEKTRO",
    32: "D4 TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR",
}

# Deskripsi Prodi
PRODI_DESCRIPTORS = {
    1: "Pariwisata, manajemen pariwisata, destinasi wisata, industri perhotelan, tour guide, S1",
    2: "Manajemen, strategi bisnis, pengelolaan organisasi, keuangan, pemasaran, S1",
    3: "Ekonomi pembangunan, kebijakan ekonomi, analisis ekonomi, pembangunan sosial, S1",
    4: "Akuntansi, laporan keuangan, audit, perpajakan, S1",
    5: "Akuntansi Perpajakan, perpajakan, audit pajak, akuntansi keuangan, D4",
    6: "Akuntansi, pengelolaan keuangan, pajak, audit, D3",
    7: "Pendidikan Bahasa Inggris, pengajaran bahasa Inggris, metodologi, S2",
    8: "Pendidikan Bahasa Indonesia, pengajaran bahasa Indonesia, kebudayaan, S2",
    9: "Pendidikan Matematika, pengajaran matematika, pendidikan dasar, S1",
    10: "Pendidikan Ilmu Pengetahuan Alam, pengajaran IPA, pengembangan sains, S1",
    11: "Pendidikan Biologi, pengajaran biologi, laboratorium biologi, S1",
    12: "Pendidikan Bahasa Inggris, pengajaran bahasa Inggris, S1",
    13: "Pendidikan Bahasa dan Sastra Indonesia, pengajaran bahasa dan sastra, S1",
    14: "Pendidikan Profesi Guru, profesi guru, pendidikan tinggi, S1",
    15: "Administrasi Publik, kebijakan publik, manajemen pemerintahan, S2",
    16: "Ilmu Komunikasi, komunikasi massa, media, jurnalistik, S1",
    17: "Ilmu Administrasi Negara, manajemen publik, kebijakan publik, S1",
    18: "Hukum, hukum perdata, hukum pidana, S1",
    19: "Teknologi Pangan, ilmu pangan, teknologi olahan pangan, S1",
    20: "Peternakan, manajemen peternakan, kesehatan ternak, S1",
    21: "Gizi, ilmu gizi, dietetik, kesehatan masyarakat, S1",
    22: "Akuakultur, budidaya perikanan, kelautan, S1",
    23: "Agroteknologi, pertanian, teknologi pertanian, S1",
    24: "Agribisnis, bisnis pertanian, pemasaran hasil pertanian, S1",
    25: "Farmasi, ilmu farmasi, farmakologi, D3",
    26: "Teknologi Informasi, sistem informasi, pengembangan perangkat lunak, S1",
    27: "Teknik Sipil, konstruksi, struktur bangunan, transportasi, S1",
    28: "Teknik Mesin, desain mesin, manufaktur, otomotif, S1",
    29: "Teknik Mekatronika, robotik, otomatisasi, teknologi mekanik, S1",
    30: "Teknik Industri, manajemen produksi, optimasi proses, S1",
    31: "Teknik Elektro, elektronik, listrik, sistem kontrol, S1",
    32: "Teknologi Rekayasa Perancangan Manufaktur, desain produk, manufaktur, D4",
}

# Domain keywords untuk setiap prodi
DOMAIN = {
    "gizi": ["gizi", "nutrisi", "diet", "makanan sehat", "kalori", "vitamin", "mineral", 
             "status gizi", "kebutuhan gizi", "ilmu gizi", "dietetik", "gizi masyarakat",
             "penilaian gizi", "konsultasi gizi", "penyuluhan gizi", "gizi klinik"],
    
    "akuntansi": ["akuntansi", "keuangan", "audit", "pajak", "laporan keuangan", "perpajakan",
                  "auditing", "akuntan", "pembukuan", "akuntansi keuangan", "akuntansi manajemen",
                  "auditor", "pajak penghasilan", "pajak pertambahan nilai", "perpajakan indonesia"],
    
    "teknologi_informasi": ["teknologi informasi", "programming", "coding", "software", "aplikasi",
                           "sistem informasi", "database", "web", "mobile", "java", "python",
                           "javascript", "php", "html", "css", "it", "teknologi digital",
                           "artificial intelligence", "machine learning", "data mining", "big data",
                           "internet of things", "cloud computing", "cyber security", "blockchain"],
    
    "pendidikan_bahasa_inggris": ["bahasa inggris", "english", "teaching english", "efl", "esl",
                                 "language teaching", "english education", "pengajaran bahasa inggris",
                                 "english proficiency", "toefl", "ielts", "speaking english",
                                 "writing english", "reading comprehension", "english grammar"],
    
    "teknik_mesin": ["teknik mesin", "mesin", "engineering", "mekanik", "thermodinamika",
                    "fluida", "motor bakar", "konversi energi", "desain mesin", "manufaktur",
                    "cad cam", "elemen mesin", "vibrasi", "perawatan mesin", "otomasi industri"],
    
    "pariwisata": ["pariwisata", "wisata", "tourisme", "hotel", "hospitality", "destinasi wisata",
                  "tour guide", "pemanduan wisata", "manajemen pariwisata", "industri pariwisata",
                  "wisata budaya", "ekowisata", "hotel management", "resort", "travel"],
    
    "manajemen": ["manajemen", "management", "bisnis", "strategi bisnis", "organisasi", "pemasaran",
                 "manajemen strategi", "kepemimpinan", "manajemen operasi", "manajemen sumber daya manusia",
                 "manajemen pemasaran", "manajemen keuangan", "business plan", "strategi pemasaran"],
    
    "hukum": ["hukum", "law", "legal", "perdata", "pidana", "konstitusi", "hak asasi",
             "hukum internasional", "hukum bisnis", "hukum pidana", "hukum perdata",
             "hukum tata negara", "hukum administrasi negara", "hukum islam", "fiqih"],
    
    "farmasi": ["farmasi", "farmakologi", "obat", "medis", "kesehatan", "apoteker",
               "farmasi klinik", "farmasetika", "kimia farmasi", "teknologi farmasi",
               "formulasi obat", "stabilitas obat", "farmakokinetik", "farmakodinamik"],
    
    "pertanian": ["pertanian", "agrikultur", "tanaman", "budidaya", "agribisnis", "agroteknologi",
                 "hortikultura", "tanaman pangan", "tanaman perkebunan", "ilmu tanah",
                 "pupuk", "pestisida", "irigasi", "pertanian organik", "hidroponik"],
    
    "ekonomi_pembangunan": ["ekonomi pembangunan", "pembangunan ekonomi", "ekonomi regional",
                           "pertumbuhan ekonomi", "pembangunan berkelanjutan", "ekonomi indonesia",
                           "kebijakan ekonomi", "pembangunan sosial", "ekonomi makro"],
    
    "pendidikan_matematika": ["pendidikan matematika", "pembelajaran matematika", "matematika sekolah",
                             "aljabar", "kalkulus", "geometri", "statistika", "probabilitas",
                             "matematika dasar", "numerik", "trigonometri"],
    
    "pendidikan_ipa": ["pendidikan ipa", "ilmu pengetahuan alam", "sains", "fisika", "kimia", "biologi",
                      "pembelajaran ipa", "laboratorium ipa", "eksperimen sains", "metode ilmiah"],
    
    "pendidikan_biologi": ["pendidikan biologi", "biologi sel", "genetika", "ekologi", "anatomi",
                          "fisiologi", "mikrobiologi", "zoologi", "botani", "biologi molekuler"],
    
    "ilmu_komunikasi": ["ilmu komunikasi", "komunikasi massa", "jurnalistik", "public relations",
                       "media", "broadcasting", "komunikasi pemasaran", "komunikasi organisasi",
                       "komunikasi interpersonal", "persuasi", "retorika"],
    
    "administrasi_publik": ["administrasi publik", "kebijakan publik", "pemerintahan", "pelayanan publik",
                           "birokrasi", "governance", "administrasi negara", "manajemen publik",
                           "otonomi daerah", "desentralisasi"],
    
    "teknik_sipil": ["teknik sipil", "konstruksi", "struktur", "bangunan", "jalan", "jembatan",
                    "transportasi", "sipil", "beton", "baja", "geoteknik", "hidrolika",
                    "manajemen konstruksi", "survey", "rekayasa struktur"],
    
    "teknik_elektro": ["teknik elektro", "listrik", "elektronika", "kontrol", "instrumentasi",
                      "tenaga listrik", "sistem daya", "telekomunikasi", "sinyal", "digital",
                      "mikrokontroler", "arduino", "robotika", "automation"],
    
    "teknik_industri": ["teknik industri", "optimasi", "produksi", "operasi", "quality control",
                       "ergonomi", "sistem kerja", "manajemen kualitas", "logistik", "supply chain",
                       "perancangan sistem", "analisis sistem"],
    
    "peternakan": ["peternakan", "ternak", "hewan", "sapi", "ayam", "kambing", "domba",
                  "pakan ternak", "kesehatan hewan", "produksi ternak", "reproduksi ternak",
                  "manajemen peternakan", "unggas", "susu", "daging"],
    
    "akuakultur": ["akuakultur", "budidaya perairan", "perikanan", "ikan", "udang", "kerang",
                  "budidaya ikan", "akuarium", "tambak", "hatchery", "pembenihan", "kualitas air"],
    
    "teknologi_pangan": ["teknologi pangan", "pangan", "makanan", "pengolahan pangan", "keamanan pangan",
                        "gizi pangan", "pengawetan makanan", "mikrobiologi pangan", "analisis pangan",
                        "standar mutu pangan", "food safety"]
}

# Fungsi untuk menormalisasi teks (menghapus spasi berlebih dan mengubah ke huruf kecil)
def normalize(text: str) -> str:
    return re.sub(r"\s+", " ", (text or "")).strip().lower()

# Fungsi untuk memeriksa apakah ada kata kunci dalam teks
def has_any(text: str, keywords) -> bool:
    t = normalize(text)
    return any(k in t for k in keywords)

# Fungsi untuk mendeteksi format CSV
def sniff_dialect(sample: bytes):
    """
    Menyusun deteksi format CSV menggunakan Sniffer dari modul csv.
    """
    try:
        sample_text = sample.decode("utf-8-sig")
    except Exception:
        sample_text = sample.decode("utf-8", errors="ignore")
    
    # Gunakan Sniffer untuk mendeteksi dialect (delimiter)
    sniffer = csv.Sniffer()
    try:
        dialect = sniffer.sniff(sample_text, delimiters=",;\t|")
    except Exception:
        class _D(csv.excel):
            delimiter = ","  # Default ke ',' jika gagal mendeteksi
        dialect = _D()
    
    return dialect

# Fungsi untuk membaca file CSV fleksibel
def read_csv_flexible(path: str) -> List[Dict]:
    with open(path, "rb") as fb:
        sample = fb.read(4096)  # Membaca sebagian file untuk deteksi format
        dialect = sniff_dialect(sample)  # Memanggil fungsi sniff_dialect
    
    rows = []
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.reader(f, dialect)  # Menggunakan dialect yang terdeteksi
        try:
            fieldnames = next(reader)  # Ambil header dari CSV
        except StopIteration:
            return rows
        fieldnames_norm = [normalize(h) for h in fieldnames]  # Normalisasi header
        idx_id = alias_index(fieldnames_norm, "biblio_id")
        idx_title = alias_index(fieldnames_norm, "title")
        idx_topic = alias_index(fieldnames_norm, "topic")  # Kolom topic

        for r in reader:
            if not r:
                continue
            bid = r[idx_id].strip() if idx_id is not None else ""
            tit = r[idx_title].strip() if idx_title is not None else ""
            top = r[idx_topic].strip() if idx_topic is not None else ""  # Ambil topic
            if bid and tit:
                rows.append({"biblio_id": bid, "title": tit, "topic": top})  # Menyertakan topic
    return rows

# Fungsi untuk mencari indeks berdasarkan alias
def alias_index(fieldnames_norm: List[str], target: str) -> Optional[int]:
    """
    Fungsi ini mencari indeks kolom berdasarkan alias nama yang diberikan (seperti 'biblio_id', 'title', 'topic')
    dalam daftar nama kolom yang telah dinormalisasi (fieldnames_norm).
    """
    HEADER_ALIASES = {
        "biblio_id": {"biblio_id", "id", "biblio id", "biblioid"},
        "title": {"title", "judul", "book_title"},
        "topic": {"topic", "kategori", "subject", "topik"},
    }
    
    wanted = HEADER_ALIASES.get(target, set())
    
    for i, name in enumerate(fieldnames_norm):
        if name in wanted:
            return i
    return None

# Fungsi untuk melakukan pemetaan prodi berdasarkan title dan topic
def rule_based_prodi_multi(title: str, topic: str) -> Set[int]:
    t = re.sub(r"\s+", " ", (title or "")).strip().lower()
    topic_normalized = re.sub(r"\s+", " ", (topic or "")).strip().lower()
    chosen: Set[int] = set()

    # Mencocokkan berdasarkan domain dan cue dari title dan topic
    if has_any(t, DOMAIN["gizi"]) or has_any(topic, DOMAIN["gizi"]):
        chosen |= {21}  # Prodi Gizi
    
    if has_any(t, DOMAIN["akuntansi"]) or has_any(topic, DOMAIN["akuntansi"]):
        chosen |= {4, 5, 6}  # Prodi Akuntansi
    
    if has_any(t, DOMAIN["teknologi_informasi"]) or has_any(topic, DOMAIN["teknologi_informasi"]):
        chosen |= {26}  # Prodi Teknologi Informasi
    
    if has_any(t, DOMAIN["pendidikan_bahasa_inggris"]) or has_any(topic, DOMAIN["pendidikan_bahasa_inggris"]):
        chosen |= {7, 12}  # Pendidikan Bahasa Inggris
    
    if has_any(t, DOMAIN["teknik_mesin"]) or has_any(topic, DOMAIN["teknik_mesin"]):
        chosen |= {28}  # Teknik Mesin
    
    if has_any(t, DOMAIN["pariwisata"]) or has_any(topic, DOMAIN["pariwisata"]):
        chosen |= {1}  # Pariwisata
    
    if has_any(t, DOMAIN["manajemen"]) or has_any(topic, DOMAIN["manajemen"]):
        chosen |= {2}  # Manajemen
    
    if has_any(t, DOMAIN["hukum"]) or has_any(topic, DOMAIN["hukum"]):
        chosen |= {18}  # Hukum
    
    if has_any(t, DOMAIN["farmasi"]) or has_any(topic, DOMAIN["farmasi"]):
        chosen |= {25}  # Farmasi
    
    if has_any(t, DOMAIN["pertanian"]) or has_any(topic, DOMAIN["pertanian"]):
        chosen |= {23, 24}  # Agroteknologi dan Agribisnis
    
    if has_any(t, DOMAIN["ekonomi_pembangunan"]) or has_any(topic, DOMAIN["ekonomi_pembangunan"]):
        chosen |= {3}  # Ekonomi Pembangunan
    
    if has_any(t, DOMAIN["pendidikan_matematika"]) or has_any(topic, DOMAIN["pendidikan_matematika"]):
        chosen |= {9}  # Pendidikan Matematika
    
    if has_any(t, DOMAIN["pendidikan_ipa"]) or has_any(topic, DOMAIN["pendidikan_ipa"]):
        chosen |= {10}  # Pendidikan IPA
    
    if has_any(t, DOMAIN["pendidikan_biologi"]) or has_any(topic, DOMAIN["pendidikan_biologi"]):
        chosen |= {11}  # Pendidikan Biologi
    
    if has_any(t, DOMAIN["ilmu_komunikasi"]) or has_any(topic, DOMAIN["ilmu_komunikasi"]):
        chosen |= {16}  # Ilmu Komunikasi
    
    if has_any(t, DOMAIN["administrasi_publik"]) or has_any(topic, DOMAIN["administrasi_publik"]):
        chosen |= {15, 17}  # Administrasi Publik dan Ilmu Administrasi Negara
    
    if has_any(t, DOMAIN["teknik_sipil"]) or has_any(topic, DOMAIN["teknik_sipil"]):
        chosen |= {27}  # Teknik Sipil
    
    if has_any(t, DOMAIN["teknik_elektro"]) or has_any(topic, DOMAIN["teknik_elektro"]):
        chosen |= {31}  # Teknik Elektro
    
    if has_any(t, DOMAIN["teknik_industri"]) or has_any(topic, DOMAIN["teknik_industri"]):
        chosen |= {30}  # Teknik Industri
    
    if has_any(t, DOMAIN["peternakan"]) or has_any(topic, DOMAIN["peternakan"]):
        chosen |= {20}  # Peternakan
    
    if has_any(t, DOMAIN["akuakultur"]) or has_any(topic, DOMAIN["akuakultur"]):
        chosen |= {22}  # Akuakultur
    
    if has_any(t, DOMAIN["teknologi_pangan"]) or has_any(topic, DOMAIN["teknologi_pangan"]):
        chosen |= {19}  # Teknologi Pangan

    # Jika tidak ada pencocokan sama sekali, berikan beberapa prodi umum sebagai fallback
    if not chosen:
        # Fallback ke prodi yang lebih umum berdasarkan kata kunci umum
        if any(word in t for word in ["pendidikan", "pengajaran", "belajar", "mengajar"]):
            chosen |= {9, 10, 11, 12, 13}  # Prodi pendidikan
        elif any(word in t for word in ["teknik", "engineering", "teknologi"]):
            chosen |= {26, 27, 28, 29, 30, 31, 32}  # Prodi teknik
        elif any(word in t for word in ["ekonomi", "bisnis", "manajemen", "pemasaran"]):
            chosen |= {2, 3, 4}  # Prodi ekonomi dan bisnis
        else:
            chosen |= {26}  # Default fallback ke Teknologi Informasi

    return chosen

# Main function
def main():
    ap = argparse.ArgumentParser(description="Classify (multi-label) search_biblio titles into multiple prodi IDs.")
    ap.add_argument("--input", required=True, help="Path to search_biblio.csv or search_biblio.sql")
    ap.add_argument("--output-csv", default="classifications.csv", help="Output CSV path (biblio_id,prodi_id rows)")
    ap.add_argument("--verbose", action="store_true", help="Show detailed processing information")
    args = ap.parse_args()

    rows = read_csv_flexible(args.input)
    print(f"Loaded {len(rows)} rows with biblio_id + title + topic.")

    pair_rows = []
    classification_stats = {}
    
    for i, r in enumerate(rows):
        if args.verbose and i % 1000 == 0:
            print(f"Processing row {i}/{len(rows)}...")
        
        pset = rule_based_prodi_multi(r["title"], r["topic"])
        
        # Statistics
        num_prodi = len(pset)
        classification_stats[num_prodi] = classification_stats.get(num_prodi, 0) + 1

        for pid in pset:
            pair_rows.append((str(r["biblio_id"]), pid))

    with open(args.output_csv, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(["biblio_id", "prodi_id"])
        for bid, pid in pair_rows:
            w.writerow([bid, pid])

    # Print statistics
    print(f"\nClassification Statistics:")
    print(f"Input rows: {len(rows)}")
    print(f"Output rows: {len(pair_rows)}")
    print(f"Multi-label ratio: {len(pair_rows)/len(rows):.2f}x")
    
    print(f"\nDistribution of number of prodi per title:")
    for num_prodi in sorted(classification_stats.keys()):
        count = classification_stats[num_prodi]
        percentage = (count / len(rows)) * 100
        print(f"  {num_prodi} prodi: {count} titles ({percentage:.1f}%)")
    
    print(f"\nDone. Wrote: {args.output_csv}")

if __name__ == "__main__":
    main()