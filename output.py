import os
import subprocess
import numpy as np

def run_xfoil(airfoil_file, alpha=5.0, Re=1e6, Mach=0.1):
    """
    使用 XFOIL 計算指定攻角下的 Cl, Cd, L/D。
    :param airfoil_file: 翼型 .dat 文件的路徑
    :param alpha: 攻角（度）
    :param Re: 雷諾數
    :param Mach: 馬赫數
    :return: (Cl, Cd, L/D) 或 (None, None, None) 若計算失敗
    """
    airfoil_path = os.path.abspath(airfoil_file)
    polar_file = "polar.txt"

    if os.path.exists(polar_file):
        os.remove(polar_file)

    xfoil_commands = f"""
LOAD {airfoil_path}
PANE
GDES
CADD 0.01
EXEC
OPER
Visc {Re} 
Mach {Mach}
PACC
{polar_file}

ALFA {alpha}
PACC
QUIT
"""
    process = subprocess.run(
        ["xfoil"], input=xfoil_commands.encode(),
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )

    if process.returncode != 0:
        print(f"❌ XFOIL 運行失敗: {airfoil_file}\n錯誤信息: {process.stderr.decode()}")
        return None, None, None

    try:
        with open(polar_file, "r") as f:
            lines = f.readlines()
            if len(lines) < 2:
                print(f"⚠️ XFOIL 無輸出數據: {airfoil_file}")
                return None, None, None

            last_line = lines[-1].split()
            Cl, Cd = float(last_line[1]), float(last_line[2])
            LD_ratio = Cl / Cd
            return Cl, Cd, LD_ratio
    except Exception as e:
        print(f"❌ 無法讀取 polar.txt: {airfoil_file}, 錯誤: {e}")
        return None, None, None


def load_airfoil(airfoil_file):
    """
    讀取翼型 .dat 文件，返回 (x, y) 座標
    :param airfoil_file: .dat 文件路徑
    :return: (x_coords, y_coords) 或 (None, None) 若格式錯誤
    """
    with open(airfoil_file, "r") as f:
        lines = f.readlines()

    # 找到數據開始行（跳過標題行）
    data_start = 0
    while data_start < len(lines):
        try:
            float(lines[data_start].split()[0])
            break
        except ValueError:
            data_start += 1

    try:
        coords = np.genfromtxt(lines[data_start:])
        if coords.ndim != 2 or coords.shape[1] not in [2, 3]:
            raise ValueError("翼型數據格式錯誤")

        # 如果有三列，去掉第三列
        if coords.shape[1] == 3:
            coords = coords[:, :2]

        return coords[:, 0], coords[:, 1]
    except Exception as e:
        print(f"❌ 無法讀取 {airfoil_file}: {e}")
        return None, None


# 設定條件
alpha = 5.0
Re = 1e6
Mach = 0.1
airfoil_dir = "airfoils/xfoil_format/"
output_dir = "data"

os.makedirs(output_dir, exist_ok=True)

airfoil_files = [f for f in os.listdir(airfoil_dir) if f.endswith(".dat")]

for airfoil in airfoil_files:
    airfoil_path = os.path.join(airfoil_dir, airfoil)

    Cl, Cd, LD = run_xfoil(airfoil_path, alpha, Re, Mach)
    x_coords, y_coords = load_airfoil(airfoil_path)

    if Cl is None or Cd is None or LD is None or x_coords is None:
        print(f"❌ 模擬失敗: {airfoil}")
        continue

    npz_filename = airfoil.replace(".dat", ".npz")
    np.savez(os.path.join(output_dir, npz_filename), x=x_coords, y=y_coords, Cl=Cl, Cd=Cd, LD=LD)

    print(f"✅ 儲存: {npz_filename}, Cl = {Cl:.4f}, Cd = {Cd:.4f}, L/D = {LD:.2f}")
