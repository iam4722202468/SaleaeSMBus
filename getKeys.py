from saleae import Saleae, PerformanceOption
import time
import csv
import pickle

def runCapture(host='localhost', port=10429):
        s = Saleae(host=host, port=port)
        print("Saleae connected.")

        devices = s.get_connected_devices()
        print("Connected devices:")

        digital = [0,1,2,3,4]
        analog = []

        digital, analog = s.get_active_channels()
        print("Reading back active channels:")
        print("\tdigital={}\n\tanalog={}".format(digital, analog))

        s.set_num_samples(170000000)
        rate = s.set_sample_rate_by_minimum(4e6 * 3, 0)
        print("\tSet to", rate)

        print("Starting a capture")

        s.capture_start()

        while not s.is_processing_complete():
            print("\t..waiting for capture to complete")
            time.sleep(1)

        print("Capture complete")

        analyzers = s.get_analyzers()
        s.export_analyzer(analyzers[0][1], './out.csv')
        time.sleep(2)

replyLists = []

with open('data.pkl', 'rb') as input:
    replyLists = pickle.load(input)

for x in replyLists:
    print(x)

def parseCapture():
    inside60 = False
    insideReply = False

    caughtCode = []
    caughtReply = []

    with open('./out.csv', 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        headers = next(reader, None)
        for row in reader:
            if insideReply and row[4] == 'Write':
                insideReply = False
                print([caughtCode, caughtReply])
                return
                
            if row[3] == '60' and not inside60 and row[4] == 'Write':
                inside60 = True
            elif row[3] == '60' and inside60 and row[4] == 'Write':
                inside60 = False
                insideReply = True
            else:
                if inside60:
                    caughtCode.append(row[3])
                elif insideReply:
                    caughtReply.append(row[3])

    print([caughtCode, caughtReply])

    try:
        replyLists.index([caughtCode, caughtReply])
        print('Found')
    except:
        replyLists.append([caughtCode, caughtReply])

        with open('data.pkl', 'wb') as output:
            pickle.dump(replyLists, output, pickle.HIGHEST_PROTOCOL)

#runCapture()
#parseCapture()
