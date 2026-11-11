# Analisis Data Premier League (2006/07–2017/18)

Project Python untuk mengolah dua dataset:
- `data/stats.csv`: statistik klub per musim (240 baris, 42 kolom pada file awal).
- `data/results.csv`: hasil pertandingan (4.560 baris, 6 kolom pada file awal).

## 1. Persiapan di VS Code

1. Ekstrak folder project ini.
2. Buka folder `Premier_League_Analysis` melalui VS Code (`File > Open Folder`).
3. Pastikan Python 3.10 atau yang lebih baru sudah terpasang.
4. Buka terminal VS Code (`Terminal > New Terminal`).
5. Buat virtual environment:

   **Windows**
   ```powershell
   py -m venv .venv
   .venv\Scripts\Activate.ps1
   ```

   Jika PowerShell memblokir aktivasi, gunakan Command Prompt:
   ```bat
   .venv\Scripts\activate.bat
   ```

6. Instal library:
   ```bash
   python -m pip install --upgrade pip
   pip install -r requirements.txt
   ```
7. Jalankan analisis:
   ```bash
   python analysis.py
   ```

## 2. Hasil yang dibuat

- `outputs/tables/`: ringkasan kualitas data, statistik deskriptif, kuartil/desil/persentil, top 10 gol, distribusi hasil pertandingan, perbandingan gol kandang/tandang, dan korelasi Pearson.
- `outputs/figures/`: histogram, boxplot, top 10, diagram hasil pertandingan, perbandingan gol kandang/tandang, heatmap korelasi, scatter plot, serta grafik HTML interaktif Plotly (jika library tersedia).

Grafik PNG disimpan dengan resolusi 300 DPI agar cukup tajam saat dimasukkan ke PowerPoint.

## 3. Catatan metodologi

- Baris kosong tidak otomatis diisi nol, karena nilai kosong tidak selalu berarti nol.
- Analisis korelasi menggunakan variabel yang lengkap pada seluruh 240 catatan klub-musim.
- `stats.csv` dianalisis pada tingkat klub-musim, sedangkan `results.csv` pada tingkat pertandingan.
- Korelasi menunjukkan hubungan linear, bukan bukti sebab-akibat.
