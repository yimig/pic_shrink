import io
import os
import threading
import time
from PIL import Image


def shrink_picture(file, target_path, is_clean_background):
    image = Image.open(file)
    if is_clean_background:
        image = convert_background(image, (255, 255, 255))
    try:
        result_image, quality, resize_arg, size = shrink_to_size(image, 5000)
        create_directory(target_path)
        result_image.save(target_path, format="jpeg", quality=quality, optimize=True)
        print(file + " Done, quality:" + str(quality) + "; resize_arg:" + str(resize_arg) + "; size:" + str(size) + ";")
        return True
    except Exception as Argument:
        print("Error in " + file + " Cause: " + str(Argument))
        return False


def convert_background(image, bg_rgb):
    background = Image.new('RGBA', image.size, bg_rgb)
    return Image.alpha_composite(background, image).convert("L")


def shrink_to_size(image, target_size):
    quality = 96
    resize_arg = 1
    flag = True
    while True:
        result_image, size = reshrink(image, quality, resize_arg)
        if size > target_size:
            flag, quality, resize_arg = reduce_quality(flag, quality, resize_arg)
            if quality <= 0 or resize_arg <= 0:
                raise Exception("错误：压缩参数已经耗尽，无法继续压缩")
        else:
            break
    return result_image, quality, resize_arg, size


def reduce_quality(flag, quality, resize_arg):
    if flag:
        quality -= 2
        flag = quality % 10 != 0
    else:
        resize_arg -= 0.1
        flag = True
    return flag, quality, resize_arg


def reshrink(image, quality, resize_arg):
    x, y = image.size
    image = image.resize((int(x * resize_arg), int(y * resize_arg)), Image.ANTIALIAS)
    return image, get_picture_actual_size(image, quality)


def get_picture_actual_size(image, quality):
    buf = io.BytesIO()
    buf.seek(0)
    image.save(buf, format='jpeg', quality=quality, optimize=True)
    res = buf.tell()
    buf.close()
    return res


def shrink_directory(source: str, target: str):
    global target_list
    for filepath, dirnames, filenames in os.walk(source):
        for filename in filenames:
            if len(filename.split('.')) > 1:
                if filename.split('.')[-1] in ['png', 'jpg']:
                    target_list.append({
                        'source': filepath + "\\" + filename,
                        'target': target + "\\" + filepath + "\\" + filename.split('.')[0] + ".jpg",
                        'is_fill_background': filename.split('.')[-1] not in ['jpg']
                    })
                else:
                    print("\n file not support: \"" + filename + "\" in \"" + filepath + "\"\n")
    print("All Done!\n success item: " + str(success_count) + "\n error item: " + str(error_count) + "\n sum:" + str(
        success_count + error_count))


def create_directory(target: str):
    path = os.path.dirname(target)
    if not os.path.exists(path):
        os.makedirs(path)


corsor = 0
target_list = []
success_count = 0
error_count = 0
thread_count = 16
start_time = None


def thread_action():
    global corsor, success_count, error_count
    now_corsor = corsor
    if now_corsor > len(target_list)-1:
        print("Thread Quit")
        test_last_thread()
        return
    corsor += 1
    if shrink_picture(target_list[now_corsor]['source'],
                      target_list[now_corsor]['target'],
                      target_list[now_corsor]['is_fill_background']):
        success_count += 1
    else:
        error_count += 1
    thread_action()


def test_last_thread():
    global thread_count, success_count, error_count,start_time
    thread_count -= 1
    if thread_count == 0:
        print("Thread Quit: Action \n success item: " + str(success_count) +
              "\n error item: " + str(error_count) +
              "\n sum: " + str(success_count + error_count) +
              "\n time interval: " + str(time.time() - start_time))


def create_thread():
    global thread_count
    for i in range(thread_count):
        t = threading.Thread(target=thread_action)
        t.start()


if __name__ == '__main__':
    start_time = time.time()
    shrink_directory("img", "dist")
    create_thread()


    # if shrink_picture(filepath + "\\" + filename,
    #                   target + "\\" + filepath + "\\" + filename.split('.')[0] + ".jpg",
    #                   filename.split('.')[-1] not in ['jpg']):
    #     success_count += 1
    # else:
    #     error_count += 1
    # corsor += 1