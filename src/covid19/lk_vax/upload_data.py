"""Upload data to weather_lk:data branch."""

from covid19.lk_vax import epid

if __name__ == '__main__':
    epid._dump()
    epid._dump_summary()
