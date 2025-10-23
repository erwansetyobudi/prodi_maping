#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
import csv
import re
from typing import Dict, List, Optional, Tuple

# Mapping prodi berdasarkan inst_name
PRODI_MAPPING = {
    # S1 PARIWISATA
    "S1 PARIWISATA": 1,
    "PARIWISATA S1": 1,
    "S1-ILMU PARIWISATA": 1,
    
    # S1 MANAJEMEN
    "S1 MANAJEMEN": 2,
    "MANAJEMEN S1": 2,
    "S1-MANAJEMEN": 2,
    
    # S1 EKONOMI PEMBANGUNAN
    "S1 EKONOMI PEMBANGUNAN": 3,
    "EKONOMI PEMBANGUNAN S1": 3,
    "S1-EKONOMI PEMBANGUNAN": 3,
    
    # S1 AKUNTANSI
    "S1 AKUNTANSI": 4,
    "AKUNTANSI S1": 4,
    "S1-AKUNTANSI": 4,
    
    # D4 AKUNTANSI PERPAJAKAN
    "D4 AKUNTANSI PERPAJAKAN": 5,
    "AKUNTANSI PERPAJAKAN D4": 5,
    "D4-AKUNTANSI PERPAJAKAN": 5,
    
    # D3 AKUNTANSI
    "D3 AKUNTANSI": 6,
    "AKUNTANSI D3": 6,
    "D3-AKUNTANSI": 6,
    
    # S2 PENDIDIKAN BAHASA INGGRIS
    "S2 PENDIDIKAN BAHASA INGGRIS": 7,
    "PENDIDIKAN BAHASA INGGRIS S2": 7,
    "S2-PENDIDIKAN BAHASA INGGRIS": 7,
    
    # S2 PENDIDIKAN BAHASA INDONESIA
    "S2 PENDIDIKAN BAHASA INDONESIA": 8,
    "PENDIDIKAN BAHASA INDONESIA S2": 8,
    "S2-PENDIDIKAN BAHASA INDONESIA": 8,
    
    # S1 PENDIDIKAN MATEMATIKA
    "S1 PENDIDIKAN MATEMATIKA": 9,
    "PENDIDIKAN MATEMATIKA S1": 9,
    "S1-PENDIDIKAN MATEMATIKA": 9,
    
    # S1 PENDIDIKAN ILMU PENGETAHUAN ALAM
    "S1 PENDIDIKAN ILMU PENGETAHUAN ALAM": 10,
    "PENDIDIKAN IPA S1": 10,
    "S1-PENDIDIKAN IPA": 10,
    "S1 PENDIDIKAN IPA": 10,
    
    # S1 PENDIDIKAN BIOLOGI
    "S1 PENDIDIKAN BIOLOGI": 11,
    "PENDIDIKAN BIOLOGI S1": 11,
    "S1-PENDIDIKAN BIOLOGI": 11,
    
    # S1 PENDIDIKAN BAHASA INGGRIS
    "S1 PENDIDIKAN BAHASA INGGRIS": 12,
    "PENDIDIKAN BAHASA INGGRIS S1": 12,
    "S1-PENDIDIKAN BAHASA INGGRIS": 12,
    
    # S1 PENDIDIKAN BAHASA DAN SASTRA INDONESIA
    "S1 PENDIDIKAN BAHASA DAN SASTRA INDONESIA": 13,
    "PENDIDIKAN BAHASA INDONESIA S1": 13,
    "S1-PENDIDIKAN BAHASA INDONESIA": 13,
    
    # PENDIDIKAN PROFESI GURU
    "PENDIDIKAN PROFESI GURU": 14,
    "PPG": 14,
    "PROFESI GURU": 14,
    
    # S2 ADMINISTRASI PUBLIK
    "S2 ADMINISTRASI PUBLIK": 15,
    "ADMINISTRASI PUBLIK S2": 15,
    "S2-ADMINISTRASI PUBLIK": 15,
    
    # S1 ILMU KOMUNIKASI
    "S1 ILMU KOMUNIKASI": 16,
    "ILMU KOMUNIKASI S1": 16,
    "S1-ILMU KOMUNIKASI": 16,
    
    # S1 ILMU ADMINISTRASI NEGARA
    "S1 ILMU ADMINISTRASI NEGARA": 17,
    "ILMU ADMINISTRASI NEGARA S1": 17,
    "S1-ILMU ADMINISTRASI NEGARA": 17,
    
    # S1 HUKUM
    "S1 HUKUM": 18,
    "HUKUM S1": 18,
    "S1-HUKUM": 18,
    
    # S1 TEKNOLOGI PANGAN
    "S1 TEKNOLOGI PANGAN": 19,
    "TEKNOLOGI PANGAN S1": 19,
    "S1-TEKNOLOGI PANGAN": 19,
    
    # S1 PETERNAKAN
    "S1 PETERNAKAN": 20,
    "PETERNAKAN S1": 20,
    "S1-PETERNAKAN": 20,
    
    # S1 GIZI
    "S1 GIZI": 21,
    "GIZI S1": 21,
    "S1-GIZI": 21,
    
    # S1 AKUAKULTUR
    "S1 AKUAKULTUR": 22,
    "AKUAKULTUR S1": 22,
    "S1-AKUAKULTUR": 22,
    
    # S1 AGROTEKNOLOGI
    "S1 AGROTEKNOLOGI": 23,
    "AGROTEKNOLOGI S1": 23,
    "S1-AGROTEKNOLOGI": 23,
    
    # S1 AGRIBISNIS
    "S1 AGRIBISNIS": 24,
    "AGRIBISNIS S1": 24,
    "S1-AGRIBISNIS": 24,
    
    # D3 FARMASI
    "D3 FARMASI": 25,
    "FARMASI D3": 25,
    "D3-FARMASI": 25,
    
    # S1 TEKNOLOGI INFORMASI
    "S1 TEKNOLOGI INFORMASI": 26,
    "TEKNOLOGI INFORMASI S1": 26,
    "S1-TEKNOLOGI INFORMASI": 26,
    "S1 TEKNIK INFORMATIKA": 26,
    "TEKNIK INFORMATIKA S1": 26,
    "S1 SISTEM INFORMASI": 26,
    
    # S1 TEKNIK SIPIL
    "S1 TEKNIK SIPIL": 27,
    "TEKNIK SIPIL S1": 27,
    "S1-TEKNIK SIPIL": 27,
    
    # S1 TEKNIK MESIN
    "S1 TEKNIK MESIN": 28,
    "TEKNIK MESIN S1": 28,
    "S1-TEKNIK MESIN": 28,
    
    # S1 TEKNIK MEKATRONIKA
    "S1 TEKNIK MEKATRONIKA": 29,
    "TEKNIK MEKATRONIKA S1": 29,
    "S1-TEKNIK MEKATRONIKA": 29,
    
    # S1 TEKNIK INDUSTRI
    "S1 TEKNIK INDUSTRI": 30,
    "TEKNIK INDUSTRI S1": 30,
    "S1-TEKNIK INDUSTRI": 30,
    
    # S1 TEKNIK ELEKTRO
    "S1 TEKNIK ELEKTRO": 31,
    "TEKNIK ELEKTRO S1": 31,
    "S1-TEKNIK ELEKTRO": 31,
    
    # D4 TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR
    "D4 TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR": 32,
    "TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR D4": 32,
    "D4-TEKNOLOGI REKAYASA PERANCANGAN MANUFAKTUR": 32,
}

# Fungsi untuk menormalisasi teks
def normalize(text: str) -> str:
    """Normalisasi teks: hapus spasi berlebih, ubah ke huruf besar"""
    if not text:
        return ""
    return re.sub(r"\s+", " ", text.strip()).upper()

# Fungsi untuk mencari prodi_id berdasarkan inst_name
def find_prodi_id(inst_name: str) -> Optional[int]:
    """Cari prodi_id berdasarkan inst_name"""
    if not inst_name:
        return None
    
    normalized_inst = normalize(inst_name)
    
    # Cari exact match terlebih dahulu
    for pattern, prodi_id in PRODI_MAPPING.items():
        if pattern in normalized_inst:
            return prodi_id
    
    # Jika tidak ditemukan exact match, cari dengan pattern matching
    patterns = {
        "PARIWISATA": 1,
        "MANAJEMEN": 2,
        "EKONOMI PEMBANGUNAN": 3,
        "AKUNTANSI": [4, 5, 6],  # Bisa S1, D4, atau D3
        "PERPAJAKAN": 5,
        "PENDIDIKAN BAHASA INGGRIS": [7, 12],  # Bisa S2 atau S1
        "PENDIDIKAN BAHASA INDONESIA": [8, 13],  # Bisa S2 atau S1
        "PENDIDIKAN MATEMATIKA": 9,
        "PENDIDIKAN IPA": 10,
        "PENDIDIKAN BIOLOGI": 11,
        "PROFESI GURU": 14,
        "ADMINISTRASI PUBLIK": 15,
        "ILMU KOMUNIKASI": 16,
        "ILMU ADMINISTRASI NEGARA": 17,
        "HUKUM": 18,
        "TEKNOLOGI PANGAN": 19,
        "PETERNAKAN": 20,
        "GIZI": 21,
        "AKUAKULTUR": 22,
        "AGROTEKNOLOGI": 23,
        "AGRIBISNIS": 24,
        "FARMASI": 25,
        "TEKNOLOGI INFORMASI": 26,
        "INFORMATIKA": 26,
        "SISTEM INFORMASI": 26,
        "TEKNIK SIPIL": 27,
        "TEKNIK MESIN": 28,
        "TEKNIK MEKATRONIKA": 29,
        "TEKNIK INDUSTRI": 30,
        "TEKNIK ELEKTRO": 31,
        "TEKNOLOGI REKAYASA": 32,
    }
    
    for pattern, prodi_id in patterns.items():
        if pattern in normalized_inst:
            # Handle multiple possibilities
            if isinstance(prodi_id, list):
                # Untuk kasus seperti Akuntansi, pilih berdasarkan jenjang
                if "D3" in normalized_inst:
                    return prodi_id[2] if len(prodi_id) > 2 else prodi_id[0]
                elif "D4" in normalized_inst:
                    return prodi_id[1] if len(prodi_id) > 1 else prodi_id[0]
                else:
                    return prodi_id[0]  # Default ke yang pertama
            else:
                return prodi_id
    
    return None

# Fungsi untuk membaca file CSV member
def read_member_csv(path: str) -> List[Dict]:
    """Baca file CSV member dengan deteksi format otomatis"""
    rows = []
    
    with open(path, "rb") as fb:
        sample = fb.read(4096)
        try:
            sample_text = sample.decode("utf-8-sig")
        except Exception:
            sample_text = sample.decode("utf-8", errors="ignore")
        
        # Deteksi delimiter
        sniffer = csv.Sniffer()
        try:
            dialect = sniffer.sniff(sample_text, delimiters=",;\t|")
        except Exception:
            dialect = csv.excel()  # Default ke CSV excel
    
    with open(path, "r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f, dialect=dialect)
        for row in reader:
            rows.append(dict(row))
    
    return rows

# Fungsi utama
def main():
    parser = argparse.ArgumentParser(description="Map members to prodi based on inst_name")
    parser.add_argument("--input", required=True, help="Path to member.csv file")
    parser.add_argument("--output", default="member_prodi_mapping.csv", help="Output CSV file path")
    parser.add_argument("--verbose", action="store_true", help="Show detailed processing information")
    args = parser.parse_args()

    # Baca data member
    print("Reading member data...")
    members = read_member_csv(args.input)
    print(f"Loaded {len(members)} members")

    # Proses mapping
    mapping_results = []
    stats = {
        "mapped": 0,
        "unmapped": 0,
        "prodi_counts": {}
    }

    for member in members:
        member_id = member.get('member_id', '')
        inst_name = member.get('inst_name', '')
        
        prodi_id = find_prodi_id(inst_name)
        
        if prodi_id:
            mapping_results.append((member_id, prodi_id))
            stats["mapped"] += 1
            stats["prodi_counts"][prodi_id] = stats["prodi_counts"].get(prodi_id, 0) + 1
            
            if args.verbose:
                print(f"✓ {member_id}: {inst_name} -> Prodi {prodi_id}")
        else:
            stats["unmapped"] += 1
            if args.verbose:
                print(f"✗ {member_id}: {inst_name} -> Tidak terpetakan")

    # Tulis hasil ke CSV
    with open(args.output, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["member_id", "prodi_id"])
        for member_id, prodi_id in mapping_results:
            writer.writerow([member_id, prodi_id])

    # Tampilkan statistik
    print(f"\n=== MAPPING STATISTICS ===")
    print(f"Total members: {len(members)}")
    print(f"Successfully mapped: {stats['mapped']} ({stats['mapped']/len(members)*100:.1f}%)")
    print(f"Unmapped: {stats['unmapped']} ({stats['unmapped']/len(members)*100:.1f}%)")
    
    print(f"\nDistribution by Prodi:")
    for prodi_id in sorted(stats["prodi_counts"].keys()):
        count = stats["prodi_counts"][prodi_id]
        print(f"  Prodi {prodi_id}: {count} members ({count/stats['mapped']*100:.1f}%)")
    
    print(f"\nOutput written to: {args.output}")

    # Tampilkan contoh yang tidak terpetakan (jika ada)
    if stats["unmapped"] > 0 and args.verbose:
        print(f"\nSample of unmapped inst_name values:")
        unmapped_samples = set()
        for member in members:
            inst_name = member.get('inst_name', '')
            if inst_name and not find_prodi_id(inst_name):
                unmapped_samples.add(inst_name)
                if len(unmapped_samples) >= 10:  # Batasi sampel yang ditampilkan
                    break
        
        for sample in sorted(unmapped_samples):
            print(f"  - '{sample}'")

if __name__ == "__main__":
    main()