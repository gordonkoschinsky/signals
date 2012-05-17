from multiprocessing import Process
import wxssignal


if __name__ == '__main__':
    p1 = Process(target=wxssignal.main, args=('S1',))
    p1.start()

    p2 = Process(target=wxssignal.main, args=('S2',), kwargs={'port':8001})
    p2.start()
