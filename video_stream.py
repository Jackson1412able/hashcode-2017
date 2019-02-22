import sys
import numpy as np

class Video():
    def __init__(self, id, size):
        self.id = id
        self.size = int(size)

class Cache():
    def __init__(self, id, storage):
        self.id = id
        self.remaining_storage = int(storage)
        self.videos = []

class Endpoint():
    def __init__(self, id, total_connected_cache, data_center_latency):
        self.id = id
        self.total_connected_cache = total_connected_cache
        self.data_center_latency = data_center_latency
        self.latency_score = {}

def parse_input(file):
    latency_lines = 0
    latency_line_index = 0
    latency_line_check = 0
    endpoint_index = 0
    request_description = []
    videos = []
    caches = []
    endpoints = []
    
    with open(file, 'r') as f:
        for i, line in enumerate(f):
            if i == 0: n_video, n_endpoint, n_request_description, n_cache, cache_size = line.split(' ')
            elif i == 1:
                x = line.split(' ') 
                for j in range(len(x)):
                    j = int(j)
                    videos.append(Video(j-1, x[j]))
            elif latency_line_check == 0 and endpoint_index < int(n_endpoint):
                latency_lines = int(line.split(' ')[1])
                endpoints.append(Endpoint(endpoint_index, latency_lines, int(line.split(' ')[0])))
                endpoint_index += 1
                print(endpoint_index)
                if latency_lines is not 0:
                    latency_line_check = 1
            elif latency_line_check == 1 and latency_line_index < latency_lines:
                endpoints[endpoint_index-1].latency_score[int(line.split(' ')[0])] = endpoints[endpoint_index-1].data_center_latency - int(line.split(' ')[1])
                latency_line_index += 1
                if latency_line_index == latency_lines:
                    latency_line_check = 0
                    latency_line_index = 0                    
            else:
                print([int(line.split(' ')[0]), int(line.split(' ')[1]), int(line.split(' ')[2])])
                request_description.append([int(line.split(' ')[0]), int(line.split(' ')[1]), int(line.split(' ')[2])])
                
    for j in range(int(n_cache)):
        caches.append(Cache(j, cache_size))
        
    return int(n_video), int(n_endpoint), int(n_request_description), int(n_cache), int(cache_size), videos, endpoints, request_description, caches
    
def sort_latency_score(endpoints):
    for x in endpoints:
        x.latency_score = dict(sorted(x.latency_score.items(), reverse=True, key= lambda x: x[1]))
        
def filter_videos(videos, cache_size):
    videos_filtered = []
    for x in videos:
        if x.size < cache_size:
            videos_filtered.append(x)
    return videos_filtered

def total_requests(request_description_sum):
    return request_description_sum[2]

def evaluate_video_cache(request_description, videos, caches, endpoints):
    for x in request_description:
        check, video_size = check_video(x[0], videos)
        if check == 1:
            fill_cache_with_video(x[0], x[1], caches, video_size, endpoints)

def check_video(video_id, video_list):
    exist = 0
    video_size = 0
    for y in video_list:
        if video_id == y.id:
            exist = 1;
            video_size = y.size
            break
    return exist, video_size

def fill_cache_with_video(video_id, endpoint_id, caches, video_size, endpoints):
    highest_latency_score_cache = 0
    highest_latency_score_cache_id = 0
    cache_id_to_fill = 0
    fill_check = 0
    for z in endpoints[endpoint_id].latency_score:     
        fill_check = check_cache_storage(z, caches, video_size, video_id, endpoint_id, endpoints)
        if fill_check == 1:
            break

def check_cache_storage(cache_id_to_fill, caches, video_size, video_id, endpoint_id, endpoints):
    for w in caches[cache_id_to_fill].videos:
        if video_id == w:
            return 0
    for r in endpoints[endpoint_id].latency_score:
        if r == video_id:
            return 0
    if caches[cache_id_to_fill].remaining_storage > video_size:
        caches[cache_id_to_fill].remaining_storage -= video_size
        caches[cache_id_to_fill].videos.append(video_id)
        fill_check = 1
    else:
        fill_check = 0
    return fill_check

def check_caches_usage(caches, cache_size):
    number_of_used_cache = 0
    for x in caches:
        if x.remaining_storage < cache_size:
            number_of_used_cache += 1
    return number_of_used_cache
    
def dump_videos(file, caches, cache_size):
    number_of_used_cache = check_caches_usage(caches, cache_size)
    with open(file, 'w') as f:
        f.write('{}\n'.format(number_of_used_cache))
        for c in caches:
            f.write('{} '.format(c.id))
            for v in c.videos:
                f.write('{} '.format(v))
            f.write('\n')
            
if __name__ == "__main__":
    n_video, n_endpoint, n_request_description, n_cache, cache_size, videos, endpoints, request_description, caches = parse_input(sys.argv[1])
    sort_latency_score(endpoints)
    videos = filter_videos(videos, cache_size)
    request_description.sort(reverse=True, key=total_requests)
    evaluate_video_cache(request_description, videos, caches, endpoints)
    dump_videos(sys.argv[2] if len(sys.argv) > 2 else 'out.txt', caches, cache_size)

