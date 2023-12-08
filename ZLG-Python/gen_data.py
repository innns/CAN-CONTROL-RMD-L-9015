import math


def calc_sin(amp, phase, sample_hz, sample_id):
    return amp * math.sin(2 * math.pi / sample_hz * sample_id + phase)


def calc_cos(amp, phase, sample_hz, sample_id):
    return amp * math.cos(2 * math.pi / sample_hz * sample_id + phase)


if __name__ == '__main__':
    with open(file="data_test_.txt", mode='w+', encoding='utf-8') as file:
        HZ = 50
        ALL_TIME = 10
        for j in range(5):
            for i in range(HZ * ALL_TIME):
                file.write("{},{},{:.3f}\n".format(i, 3, -15 + calc_sin(20, 0.85, HZ * ALL_TIME, i)))
                file.write("{},{},{:.3f}\n".format(i, 1, calc_sin(20, 0, HZ * ALL_TIME, i)))
                file.write("{},{},{:.3f}\n".format(i, 2, calc_sin(20, 0, HZ * ALL_TIME, i)))
                # file.write("{},{},{:.3f}\n".format(i, 2, calc_sin(25, 0, HZ * ALL_TIME, i)))

