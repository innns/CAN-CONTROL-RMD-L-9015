all_angles = []
tmp_angle = [0, 0, 0]
with open("circle.txt") as f:
    raw_data = f.readlines()
    for line in raw_data:
        line_data = line.strip().split(" ")
        print(line_data)
        if len(line_data) >= 5:
            m_id = int(line_data[0])
            tmp_angle[m_id - 1] = float(line_data[-1])
            if m_id == 3:
                all_angles.append(tmp_angle)
                tmp_angle = [0, 0, 0]

with open("circle.csv", "w+") as f:
    f.write("油门,横向,纵向\n")
    for tmp in all_angles:
        f.write("{},{},{}\n".format(tmp[2], tmp[0], tmp[1]))
