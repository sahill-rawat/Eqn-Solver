from keras import backend as k
from keras.models import model_from_json
import cv2
import numpy as np
k.set_image_data_format('channels_last')

json_file = open('model_rev.json', 'r')
loaded_model_json = json_file.read()
json_file.close()
loaded_model = model_from_json(loaded_model_json)
# load weights into new model
loaded_model.load_weights("model_rev.h5")

def predict(img):
    if img is not None:
        # invert image
        img = ~img
        ret, thresh = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
        ctrs, ret = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
        #  sorting on the basis of x coordinate
        cnt = sorted(ctrs, key=lambda ctr: cv2.boundingRect(ctr)[0])
        w = int(28)
        h = int(28)
        train_data = []
        rects = []
        for c in cnt:
            x, y, w, h = cv2.boundingRect(c)
            rect = [x, y, w, h]
            rects.append(rect)
        bool_rect = []
        for r in rects:
            l = []
            for rec in rects:
                flag = 0
                if rec != r:
                    if r[0] < (rec[0] + rec[2] + 10) and rec[0] < (r[0] + r[2] + 10) and r[1] < (rec[1] + rec[3] + 10) and rec[1] < (r[1] + r[3] + 10):
                        flag = 1
                    l.append(flag)
                if rec == r:
                    l.append(0)
            bool_rect.append(l)
        # remove the overlapping rectangles
        dump_rect = []
        for i in range(0, len(cnt)):
            for j in range(0, len(cnt)):
                if bool_rect[i][j] == 1:
                    area1 = rects[i][2] * rects[i][3]
                    area2 = rects[j][2] * rects[j][3]
                    if area1 == min(area1, area2):
                        dump_rect.append(rects[i])
        # Final list of rects in which actual digit/symbol is residing
        final_rect = [i for i in rects if i not in dump_rect]
        for r in final_rect:
            x = r[0]
            y = r[1]
            w = r[2]
            h = r[3]
            im_crop = thresh[y:y + h + 10, x:x + w + 10]
            im_resize = cv2.resize(im_crop, (28, 28))
            im_resize = np.reshape(im_resize, (28, 28, 1))
            train_data.append(im_resize)

    eq = ''
    for i in range(len(train_data)):
        train_data[i] = np.array(train_data[i])
        train_data[i] = train_data[i].reshape(1, 28, 28, 1)
        scores = loaded_model.predict(train_data[i])
        result = np.argmax(scores)
        # print(result)
        # labels = (1,2,3,...13)
        if result == 10:
            eq = eq + '-'
        elif result == 11:
            eq = eq + '+'
        elif result == 13:
            eq = eq + '/'
        elif result == 12:
            eq = eq + '*'
        elif result == 0:
            eq = eq + '0'
        elif result == 1:
            eq = eq + '1'
        elif result == 2:
            eq = eq + '2'
        elif result == 3:
            eq = eq + '3'
        elif result == 4:
            eq = eq + '4'
        elif result == 5:
            eq = eq + '5'
        elif result == 6:
            eq = eq + '6'
        elif result == 7:
            eq = eq + '7'
        elif result == 8:
            eq = eq + '8'
        elif result == 9:
            eq = eq + '9'

    return f"{eq} = {eval(eq)}"
