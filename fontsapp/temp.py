def canvas_image(canvasId, filename) :
    data = request.POST.__getitem__(canvas)[22:]

    #저장할 경로
    path = './media/crop/'
    day = str(font.date)[:10]
    time = str(font.date)[11:13] + "-" + str(font.date)[14:16]
    day_time = day + "_" + time
    userTime = str(request.user) + "_" + day_time + "_"    

    filename = userTime + filename + ".png"
    image = open(path+filename, 'wb')
    image.write(base64.b64decode(data))
    image.close()