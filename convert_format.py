import os

def convert_airfoil_to_xfoil_format(input_file, output_file):
    with open(input_file, "r", encoding="utf-8", errors="ignore") as f:
        lines = f.readlines()
    
    # 檢查文件是否有足夠的行數
    if len(lines) < 3:
        print(f"⚠️ 跳過 {input_file}，因為行數不足")
        return

    # 提取翼型名稱
    airfoil_name = lines[0].strip()
    
    # 處理座標數據
    raw_coords = []
    for line in lines[2:]:
        if line.strip():  # 跳過空行
            try:
                raw_coords.append(list(map(float, line.split())))
            except ValueError:
                print(f"⚠️ 警告：{input_file} 中發現無效行，跳過 -> {line.strip()}")

    # 確保至少有足夠的座標
    if len(raw_coords) < 4:
        print(f"⚠️ 跳過 {input_file}，因為座標點數不足")
        return

    # 上表面與下表面分開
    mid_index = len(raw_coords) // 2
    upper_surface = raw_coords[:mid_index]  # 上表面
    lower_surface = raw_coords[mid_index:]  # 下表面

    # 重新排序座標
    upper_surface.reverse()  # 上表面應該從後緣到前緣
    final_coords = upper_surface + lower_surface  # 連接上表面和下表面

    # 確保輸出目錄存在
    os.makedirs(os.path.dirname(output_file), exist_ok=True)

    # 寫入新格式的 `.dat` 文件
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(airfoil_name + "\n")
        for x, y in final_coords:
            f.write(f"{x:.6f} {y:.6f}\n")

    print(f"✅ 轉換完成，輸出文件: {output_file}")

# 使用方法：
source_dir = "airfoils/origin/"
output_dir = "airfoils/xfoil_format/"

for airfoil in os.listdir(source_dir):
    airfoil_path = os.path.join(source_dir, airfoil)
    output_path = os.path.join(output_dir, airfoil)
    convert_airfoil_to_xfoil_format(airfoil_path, output_path)
