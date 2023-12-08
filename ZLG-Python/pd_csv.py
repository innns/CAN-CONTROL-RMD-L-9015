import pandas as pd

# 读取CSV文件

df = pd.read_csv(r'D:\Project\test_esp_can\twai_network_master\ZLG-Python\1.csv', encoding='gb2312')

# 添加新的一列，此时新列值均为null

df['x'] = df['x'].map(float) * 3.0
print(df['x'][:10])
# 保存到新的CSV文件

df.to_csv('output.csv', index=False)
