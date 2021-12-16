from redisbloom.client import Client as RedisBloom
import sys

file_path = "formatted00.dat"
key_length = 8
packet_num = 10000000
host = "localhost"
port = 6379
password = 981026

if __name__ == "__main__":
    k = sys.argv[1]
    width = sys.argv[2]
    depth = sys.argv[3]
    decay = sys.argv[4]
    print("K=", k, "width=", width, "depth=", depth, "decay=", decay)

    rb = RedisBloom(host=host, port=port, password=password)
    rb.delete("topk")
    rb.topkReserve("topk", k, width, depth, decay)

    B = dict()
    C = dict()
    P = dict()

    with open(file_path, "rb+") as file:
        count = 0
        for i in range(int(packet_num)):
            key = file.read(key_length)
            key = key.decode(encoding='iso-8859-1')
            rb.topkAdd("topk", key)
            if key in B.keys():
                B[key] += 1
            else:
                B[key] = 1
            count += 1
            if count % (packet_num / 10) == 0: print("Inserting:", count)

    print("Number of Flows:", len(B))
    P = sorted(B.items(), key=lambda d: d[1], reverse=True)
    for i in range(int(k)):
        C[P[i][0]] = P[i][1]
    # print(C)

    AAE = 0
    ARE = 0
    sum = 0
    topk_list = rb.topkListWithCount("topk")
    # print(topk_list)
    for i in range(int(k)):
        query_key = topk_list[2 * i]
        query_value = topk_list[2 * i + 1]
        AAE += abs(B[query_key] - query_value)
        ARE += abs((B[query_key] - query_value) / B[query_key])
        if query_key in C.keys(): sum += 1

    print("Precision=", sum / int(k), "AAE=", AAE, "ARE=", ARE)
