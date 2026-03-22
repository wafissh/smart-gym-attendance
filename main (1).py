import cv2
import mediapipe as mp
from mediapipe.tasks import python
from mediapipe.tasks.python import vision
import csv
import os
import sys
from datetime import datetime

# ===== CONFIG =====
THRESHOLD = 0.7
LOG_FILE = "attendance_log.csv"
COOLDOWN_SECONDS = 10
MODEL_DETECTOR = "models/blaze_face_short_range.tflite"
MODEL_EMBEDDER = "models/mobilenet_v3_small.tflite"
DATASET_DIR = "dataset"


# ================================================================
# UTILS
# ================================================================

def check_models():
    for path in [MODEL_DETECTOR, MODEL_EMBEDDER]:
        if not os.path.exists(path):
            print(f"[ERROR] Model tidak ditemukan: {path}")
            sys.exit(1)

def check_file(path):
    if not os.path.exists(path):
        print(f"[ERROR] File tidak ditemukan: {path}")
        return False
    return True

def load_detector():
    check_models()
    opts = vision.FaceDetectorOptions(
        base_options=python.BaseOptions(model_asset_path=MODEL_DETECTOR)
    )
    return vision.FaceDetector.create_from_options(opts)

def load_embedder():
    check_models()
    opts = vision.ImageEmbedderOptions(
        base_options=python.BaseOptions(model_asset_path=MODEL_EMBEDDER),
        l2_normalize=True,
        quantize=True
    )
    return vision.ImageEmbedder.create_from_options(opts)

def init_log():
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["name", "timestamp", "similarity", "method"])
        print(f"[INFO] Log file dibuat: {LOG_FILE}")

def list_members():
    if not os.path.exists(DATASET_DIR):
        print(f"[ERROR] Folder dataset tidak ditemukan: {DATASET_DIR}")
        return []
    members = [d for d in os.listdir(DATASET_DIR)
               if os.path.isdir(os.path.join(DATASET_DIR, d))]
    return members

def pick_member(label="Pilih member"):
    members = list_members()
    if not members:
        print("[ERROR] Tidak ada member di folder dataset/")
        return None, None
    print(f"\n{label}:")
    for i, name in enumerate(members):
        print(f"  [{i+1}] {name}")
    try:
        idx = int(input("Masukkan nomor: ")) - 1
        if idx < 0 or idx >= len(members):
            raise ValueError
    except ValueError:
        print("[ERROR] Pilihan tidak valid")
        return None, None
    name = members[idx]
    folder = os.path.join(DATASET_DIR, name)
    imgs = [f for f in os.listdir(folder) if f.lower().endswith((".jpg", ".jpeg", ".png"))]
    if not imgs:
        print(f"[ERROR] Tidak ada foto di dataset/{name}/")
        return name, None
    ref_path = os.path.join(folder, imgs[0])
    return name, ref_path


# ================================================================
# MENU 1 — Test deteksi wajah dari gambar
# ================================================================

def menu_test_deteksi():
    print("\n" + "="*50)
    print("  TEST DETEKSI WAJAH DARI GAMBAR")
    print("="*50)

    path = input("Masukkan path gambar (default: test.jpg): ").strip()
    if path == "":
        path = "test.jpg"

    if not check_file(path):
        return

    detector = load_detector()

    img = cv2.imread(path)
    if img is None:
        print("[ERROR] Gagal membaca gambar")
        return

    rgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
    results = detector.detect(mp_image)

    if results.detections:
        print(f"\n[OK] Wajah terdeteksi: {len(results.detections)} wajah")
        for det in results.detections:
            bbox = det.bounding_box
            x = max(0, bbox.origin_x)
            y = max(0, bbox.origin_y)
            bw = bbox.width
            bh = bbox.height
            score = det.categories[0].score if det.categories else 0
            cv2.rectangle(img, (x, y), (x + bw, y + bh), (0, 200, 0), 2)
            cv2.putText(img, f"conf: {score:.2f}", (x, y - 8),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 200, 0), 1)
    else:
        print("\n[INFO] Tidak ada wajah terdeteksi")

    cv2.imshow("SmartGym - Face Detection Test", img)
    print("[INFO] Tekan sembarang tombol untuk menutup...")
    cv2.waitKey(0)
    cv2.destroyAllWindows()


# ================================================================
# MENU 2 — Test similarity dua foto
# ================================================================

def menu_test_similarity():
    print("\n" + "="*50)
    print("  TEST SIMILARITY DUA FOTO")
    print("="*50)

    img1_path = input("Path foto pertama: ").strip()
    img2_path = input("Path foto kedua  : ").strip()

    if not check_file(img1_path) or not check_file(img2_path):
        return

    embedder = load_embedder()

    img1 = mp.Image.create_from_file(img1_path)
    img2 = mp.Image.create_from_file(img2_path)

    emb1 = embedder.embed(img1).embeddings[0]
    emb2 = embedder.embed(img2).embeddings[0]

    similarity = vision.ImageEmbedder.cosine_similarity(emb1, emb2)

    print(f"\n  Foto 1     : {img1_path}")
    print(f"  Foto 2     : {img2_path}")
    print(f"  Similarity : {similarity:.4f}")
    print(f"  Threshold  : {THRESHOLD}")
    print(f"  Verdict    : {'SAMA (match)' if similarity >= THRESHOLD else 'BEDA (no match)'}")

    input("\nTekan Enter untuk kembali ke menu...")


# ================================================================
# MENU 3 — Daftarkan member baru
# ================================================================

def menu_daftarkan_member():
    print("\n" + "="*50)
    print("  DAFTARKAN MEMBER BARU")
    print("="*50)

    name = input("Nama member: ").strip().lower().replace(" ", "_")
    if not name:
        print("[ERROR] Nama tidak boleh kosong")
        return

    save_dir = os.path.join(DATASET_DIR, name)
    os.makedirs(save_dir, exist_ok=True)

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak bisa dibuka")
        return

    count = 0
    MAX_PHOTOS = 3
    print(f"\n[INFO] Akan mengambil {MAX_PHOTOS} foto untuk member '{name}'")
    print("[INFO] Tekan SPASI untuk ambil foto, Q untuk batal\n")

    while count < MAX_PHOTOS:
        ret, frame = cap.read()
        if not ret:
            break

        overlay = frame.copy()
        cv2.putText(overlay, f"Member: {name}", (20, 35),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 200, 0), 2)
        cv2.putText(overlay, f"Foto {count + 1}/{MAX_PHOTOS} — SPASI untuk ambil",
                    (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 1)
        cv2.imshow("SmartGym — Daftarkan Member", overlay)

        key = cv2.waitKey(1) & 0xFF
        if key == ord(" "):
            filename = os.path.join(save_dir, f"face_{count}.jpg")
            cv2.imwrite(filename, frame)
            print(f"[OK] Foto {count + 1} disimpan: {filename}")
            count += 1
        elif key == ord("q"):
            print("[INFO] Pendaftaran dibatalkan")
            break

    cap.release()
    cv2.destroyAllWindows()

    if count == MAX_PHOTOS:
        print(f"\n[OK] Member '{name}' berhasil didaftarkan ({count} foto)")
        print(f"[INFO] Foto tersimpan di: {save_dir}/")
    else:
        print(f"[INFO] Pendaftaran tidak selesai ({count}/{MAX_PHOTOS} foto)")


# ================================================================
# MENU 4 — Jalankan sistem absensi
# ================================================================

def menu_absensi():
    print("\n" + "="*50)
    print("  SISTEM ABSENSI REALTIME")
    print("="*50)

    name, ref_path = pick_member("Pilih member yang akan diabsen")
    if not name or not ref_path:
        return

    print(f"\n[INFO] Memuat referensi: {ref_path}")

    detector = load_detector()
    embedder = load_embedder()
    init_log()

    ref_img = mp.Image.create_from_file(ref_path)
    ref_embedding = embedder.embed(ref_img).embeddings[0]
    print(f"[OK] Referensi wajah '{name}' dimuat")

    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("[ERROR] Kamera tidak bisa dibuka")
        return

    last_recorded_time = None
    print("[INFO] Sistem aktif. Tekan Q untuk keluar.\n")

    while True:
        ret, frame = cap.read()
        if not ret:
            print("[ERROR] Gagal membaca frame")
            break

        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        mp_image = mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb)
        detections = detector.detect(mp_image)

        for det in detections.detections:
            bbox = det.bounding_box
            x = max(0, bbox.origin_x)
            y = max(0, bbox.origin_y)
            w = bbox.width
            h = bbox.height

            face_crop = frame[y:y+h, x:x+w]
            if face_crop.size == 0:
                continue

            face_rgb = cv2.cvtColor(face_crop, cv2.COLOR_BGR2RGB)
            face_mp = mp.Image(image_format=mp.ImageFormat.SRGB, data=face_rgb)
            emb = embedder.embed(face_mp).embeddings[0]
            similarity = vision.ImageEmbedder.cosine_similarity(ref_embedding, emb)

            now = datetime.now()

            if similarity >= THRESHOLD:
                label = f"{name} ({similarity:.2f})"
                color = (0, 200, 0)

                elapsed = (now - last_recorded_time).total_seconds() \
                    if last_recorded_time else None

                if elapsed is None or elapsed >= COOLDOWN_SECONDS:
                    with open(LOG_FILE, "a", newline="") as f:
                        writer = csv.writer(f)
                        writer.writerow([
                            name,
                            now.strftime("%Y-%m-%d %H:%M:%S"),
                            round(similarity, 3),
                            "face_recognition"
                        ])
                    last_recorded_time = now
                    print(f"[{now.strftime('%H:%M:%S')}] Check-in: {name} | "
                          f"similarity: {similarity:.3f}")
            else:
                label = f"Unknown ({similarity:.2f})"
                color = (0, 0, 200)

            cv2.rectangle(frame, (x, y), (x + w, y + h), color, 2)
            cv2.putText(frame, label, (x, y - 10),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.65, color, 2)

        cv2.putText(frame, f"Member: {name} | threshold: {THRESHOLD}",
                    (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (200, 200, 200), 1)
        cv2.imshow("SmartGym Attendance", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    print("[INFO] Sistem dihentikan.")


# ================================================================
# MENU 5 — Lihat log absensi
# ================================================================

def menu_lihat_log():
    print("\n" + "="*50)
    print("  LOG ABSENSI")
    print("="*50)

    if not os.path.exists(LOG_FILE):
        print("[INFO] Belum ada log absensi.")
        input("\nTekan Enter untuk kembali...")
        return

    with open(LOG_FILE, "r") as f:
        rows = list(csv.reader(f))

    if len(rows) <= 1:
        print("[INFO] Log masih kosong.")
        input("\nTekan Enter untuk kembali...")
        return

    header = rows[0]
    data = rows[1:]

    print(f"\n  {'No':<5} {header[0]:<20} {header[1]:<22} {header[2]:<12} {header[3]}")
    print("  " + "-"*65)
    for i, row in enumerate(data[-20:], 1):
        print(f"  {i:<5} {row[0]:<20} {row[1]:<22} {row[2]:<12} {row[3]}")

    print(f"\n  Total: {len(data)} entri (menampilkan 20 terakhir)")
    input("\nTekan Enter untuk kembali...")


# ================================================================
# MAIN MENU
# ================================================================

def main():
    while True:
        print("\n" + "="*50)
        print("  SMARTGYM ATTENDANCE SYSTEM")
        print("  Face Recognition — v1.0")
        print("="*50)
        print("  [1] Test deteksi wajah dari gambar")
        print("  [2] Test similarity dua foto")
        print("  [3] Daftarkan member baru")
        print("  [4] Jalankan sistem absensi (webcam)")
        print("  [5] Lihat log absensi")
        print("  [0] Keluar")
        print("="*50)

        choice = input("Pilih menu: ").strip()

        if choice == "1":
            menu_test_deteksi()
        elif choice == "2":
            menu_test_similarity()
        elif choice == "3":
            menu_daftarkan_member()
        elif choice == "4":
            menu_absensi()
        elif choice == "5":
            menu_lihat_log()
        elif choice == "0":
            print("\n[INFO] Keluar. Sampai jumpa!")
            sys.exit(0)
        else:
            print("[ERROR] Pilihan tidak valid, coba lagi.")


if __name__ == "__main__":
    main()
