from covid19.lk_vax import epid

def analysis():
    timeseries = epid.load_timeseries()
    print(len(timeseries))



if __name__ == '__main__':
    analysis()
