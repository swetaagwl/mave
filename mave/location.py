"""
This software downloads TMY weather file and historical weather data for 
a given location within a given time frame. It interpolates the weather 
data to a given uniform interval.

@author Taoning Wang <taoning@berkeley.edu>
@author Paul Raftery <p.raftery@berkeley.edu>
"""

import json
import urllib2
import requests
import numpy as np
from zipfile import ZipFile
from StringIO import StringIO
import os
import pkg_resources
import pkgutil
import datetime, time 
import dateutil.parser as dparser 
import pdb 
import sys 
import logging
log = logging.getLogger("mave.location")

class Location(object):
    def __init__(self, address, **kwargs):
        log.info("Assessing location string: %s"%address)
        self.lat, self.lon, self.real_addrs = self.get_latlon(address)
        log.info("Location identified as: %s"%self.real_addrs)
        self.geocode = self.get_geocode(self.lat, self.lon)
        log.info(("Geocode (nearest weather station) identified as: %s"
                  %self.geocode))

    def get_latlon(self,address):
        g_key = 'AIzaSyBHvrK5BitVyEzcTI72lObBUnqUR9L6O_E'
        address = address.replace(' ','+')
        url = \
          'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'\
                                                               %(address,g_key)
        f = json.loads(urllib2.urlopen(url).read())
        real_addrs = f['results'][0]['formatted_address']
        lat = f['results'][0]['geometry']['location']['lat']
        lon = f['results'][0]['geometry']['location']['lng']
        return lat, lon, real_addrs
       
    def get_geocode(self, lat, lon):
        w_key = 'd3dffb3b59309a05'
        url = 'http://api.wunderground.com/api/%s/geolookup/q/%s,%s.json'\
                                                       %(w_key,lat,lon)
        try:
            f = urllib2.urlopen(url)
        except:
            time.sleep(30)
            try:
                f = urllib2.urlopen(url)
            except e:
                raise e
        geoinfo = json.loads(f.read())
        geocode = geoinfo['location']['nearby_weather_stations']\
                             ['airport']['station'][0]['icao']
        if geocode == '':
            geocode = geoinfo['location']['nearby_weather_stations']['airport']\
                             ['station'][1]['icao']
        else:
            geocode = geocode
        return geocode

class Weather(object):
    def __init__(self,
                 start=None,
                 end=None,
                 key=None,
                 geocode=None,
                 interp_interval=None,
                 save=None,
                 **kwargs):
        self.start=start; self.end=end; self.interp_interval=interp_interval
        log.info(("Downloading weather data for this geocode: %s. "
                  "This may take several minutes depending of the speed "
                  "of your internet connection."
                  %geocode))
        if start > end:
            mave.error(("Start time (%s) must be before end time (%s)"
                        %(start,end)))
            raise Exception(("Start time (%s) must be before end time (%s)"
                            %(start,end)))
        else:
            dtype='datetime64[%sm]'%(interp_interval)
            self.target_dts = np.arange(
                                  start, 
                                  end,
                                  dtype=dtype).astype(datetime.datetime)
        interval = self.target_dts[-1]-self.target_dts[-2]
        self.target_dts = self.target_dts + (start-self.target_dts[0])
        if self.target_dts[-1] <= (end - interval):
            self.target_dts = np.append(self.target_dts, \
                                        self.target_dts[-1]+ interval)
        unix_vec = np.vectorize(self.str_to_unix_api)
        self.target_unix = unix_vec(self.target_dts)
        self.n_days = (end - start).days + 1
        self.count_days = 0 
        log.info(("Downloading weather data for %s days from %s to %s"
                  %(self.n_days,start,end)))
        if key == None:
            self.timestamps, self.unix, self.data = \
                                              self.get_raw(start, end, geocode)
            self.interp_data = map(lambda x: np.interp(self.target_unix,
                                        self.unix,
                                        self.data[x].astype(float)), range(0,2))
        else:
            self.timestamps, self.unix, self.data = \
                                            self.get_raw_api(start,end,\
                                                             geocode,key)

            self.interp_data = map(lambda x: np.interp(self.target_unix,
                                                    self.unix,
                                                    self.data[:,x]), range(0,2))
        if save:
            out_time = np.vstack(self.target_dts).astype(str)
            out_data = np.column_stack(self.interp_data).astype(str)
            data_frame = np.column_stack([out_time,out_data])
            np.savetxt(str(geocode)+'_weather.csv',data_frame,\
                       delimiter=',',header = self.headers,\
                       fmt ='%s',comments='')

    def get_raw(self, start, end, geocode):
        # define a range of dates
        end = end + datetime.timedelta(days=1)
        dates = np.arange(start.date(), end.date(), dtype='datetime64[D]')
        # download the timestamp data for that range of dates
        raw = np.asarray(map(lambda x: self.get_daily(geocode,x),dates))
        # stack each day of downloaded data
        data = map(lambda x: np.hstack(raw[:,x]), list([1,2]))
        timestamps = np.hstack(raw[:,0])
        # convert to unix time 
        vec_parse = np.vectorize(self.str_to_unix)
        unix = vec_parse(timestamps)
        return timestamps, unix, data

    def get_daily(self,geocode,date):
        date = date.astype(datetime.datetime)
        url = ('http://www.wunderground.com/history/airport'
              '/%s/%s/%s/%s/DailyHistory.html?format=1')%\
              (geocode,date.year,date.month,date.day)
        self.count_days += 1
        percent_progress = 100*float(self.count_days)/float(self.n_days) 
        try:
            log.info(("Downloading weather for: %s, approx %0.3f %% complete"
                      %(date,percent_progress)))
            f = urllib2.urlopen(url)
        except:
            time.sleep(30)
            try:
                f = urllib2.urlopen(url)
            except:
                raise Exception("operation stopped", date)
        raw = f.read().splitlines()
        if len(raw)<4: 
            raise Exception("No weather data for this location: ", str(raw))
        self.headers = 'time,tempF,dpF,RH'
        raw_txt = np.genfromtxt(raw,
                                delimiter=',',
                                names=self.headers,
                                usecols=('time,tempF,dpF'),
                                dtype=None,
                                skip_header=2)
        ts = raw_txt['time']
        time_series = np.ravel(np.core.defchararray.add(str(date)+' ',ts))
        raw_txt['tempF']=(raw_txt['tempF']-32)/1.8
        return time_series, raw_txt['tempF'], raw_txt['dpF']

    def str_to_unix(self,s):
        dt = dparser.parse(s)
        secs = time.mktime(dt.timetuple())
        return secs

    def get_raw_api(self, start, end, geocode, key):
        # define a range of dates
        end = end + datetime.timedelta(days=1)
        dates = np.arange(start.date(), end.date(), dtype='datetime64[D]')
        # download the timestamp data for that range of dates
        raw = np.asarray(map(lambda x: self.get_daily_api(geocode,key,x),dates))
        # stack each day of downloaded data
        data = np.vstack(raw)[:,1:4].astype(float)
        timestamps = np.vstack(raw)[:,0]
        # convert to unix time 
        vec_parse = np.vectorize(self.str_to_unix_api)
        unix = vec_parse(timestamps)
        return timestamps, unix, data

    def get_daily_api(self,geocode,key,date):
        date = date.astype(datetime.datetime)
        month = date.strftime('%m')
        day = date.strftime('%d')
        url = 'http://api.wunderground.com/api/%s/history_%s%s%s/q/%s.json'\
                               %(key,date.year,month,day,geocode)
        self.count_days += 1
        percent_progress = 100*float(self.count_days)/float(self.n_days) 
        try:
            log.info(("Downloading weatherfor: %s, approx %s %% complete"
                      %(date,percent_progress)))
            f = urllib2.urlopen(url)
        except:
            time.sleep(30)
            try:
                f = urllib2.urlopen(url)
            except:
                raise Exception("operation stopped", date)
        raw = json.loads(f.read())
        raw = raw['history']['observations']
        raw_txt = np.vstack(map(lambda x: self.parse_obs(x),raw))
        self.headers = 'time,tempF,dpF'
        return raw_txt

    def parse_obs(self,obs):
        self.dt = datetime.datetime(int(obs['date']['year']),\
                               int(obs['date']['mon']),\
                               int(obs['date']['mday']),\
                               int(obs['date']['hour']),\
                               int(obs['date']['min']))
        self.temp = obs['tempm']
        self.dewpt = obs['dewptm']
        return self.dt, self.temp, self.dewpt

    def str_to_unix_api(self,s):
        secs = time.mktime(s.timetuple())
        return secs


class TMYData(object):
    def __init__(self, 
                 location=None, 
                 year=None, 
                 interp_interval=None, 
                 use_dp=False,
                 save=None, 
                 **kwargs):
        self.use_dp = use_dp
        self.location = location
        log.info(("Downloading TMY data nearest this lat/long: %s , %s. "
                  "This may take several minutes depending of the speed "
                  "of your internet connection."
                 %(self.location.lat,self.location.lon)))
        self.tmy_file, self.cleaned_tmy = self.getTMY(self.location.lat, 
                                                      self.location.lon, 
                                                      year, 
                                                      interp_interval,
                                                      save)

    def getTMY(self,lat,lon,year,interp_interval,save):
        resource_package = __name__
        resource_path = os.path.join('data', 'epwurl.csv')
        f = pkg_resources.resource_string(resource_package, resource_path) 
        #f = StringIO(pkgutil.get_data('./mave', 'data/epwurl.csv'))
        csv = np.genfromtxt(StringIO(f), delimiter=',', dtype=None)
        csv_lat = csv[1:,4].astype(float)
        csv_lon = csv[1:,5].astype(float)
        min_idx = np.argmin(np.sqrt([(csv_lat-lat)**2+(csv_lon-lon)**2]))+1
        url = csv[min_idx,6]
        z = ZipFile(StringIO(requests.get(url).content))
        tmy_file = [i for i in z.namelist() if '.epw' in i][0]
        z.extract(tmy_file,'./')
        names = ["year","month","day","hour","minute","datasource",\
                 "DryBulb","DewPoint","RelHum","Atmos_Pressure",\
                 "ExtHorzRad","ExtDirRad","HorzIRSky","GloHorzRad",\
                 "DirNormRad","DifHorzRad","GloHorzIllum","DirNormIllum",\
                 "DifHorzIllum","ZenLum","WindDir","WindSpd","TotSkyCvr",\
                 "OpaqSkyCvr","Visibility","Clg_Hgt","Weather_obs",\
                 "Weather_code","Precip","Aerosol_Opt_Dept","Snow_Dept",\
                 "Days_Since_Last_Snow","Albedo","Liquid_Precip_Dept",\
                 "Liquid_Precip_Q"]
        if self.use_dp is False:
           cols = ','.join(names[:5])+','+names[6]
        else:
           cols = ','.join(names[:5])+','+','.join(names[6:8])
        tmy = np.genfromtxt(z.open(tmy_file), delimiter=',',\
                   dtype=None, skip_header=8, names=names, usecols=cols)
        if year is not None: 
            #np.place(tmy["year"],tmy["year"]!=datetime.datetime.now().year,\
            #         datetime.datetime.now().year)
        #else:
            np.place(tmy["year"],tmy["year"]!=year,year)
        comb_dt = np.column_stack((tmy['year'],tmy['month'],\
                                   tmy['day'],(tmy['hour']-1),\
                                   tmy['minute'])).astype(str).tolist()
        dt = map(lambda x: datetime.datetime.\
                                strptime(' '.join(x),'%Y %m %d %H %M'),\
                                comb_dt)
        unix_dt = map(lambda x: time.mktime(x.timetuple()),dt)
        target_dts = np.arange(dt[0],dt[-1],\
                               dtype='datetime64[%sm]'%(interp_interval))\
                               .astype(datetime.datetime)
        target_dts = np.append(target_dts,dt[-1])
        target_unix = map(lambda x: time.mktime(x.timetuple()),target_dts)
        interp_db = np.interp(target_unix,unix_dt,tmy['DryBulb'])
        if self.use_dp is True:
            column_names = ['LocalDateTime','OutsideDryBulbTemperature','OutsideDewPointTemperature']
            interp_dp = np.interp(target_unix,unix_dt,tmy['DewPoint'])
            cleaned_tmy = np.column_stack((target_dts,interp_db,interp_dp))
        else:
            column_names = ['LocalDateTime','OutsideDryBulbTemperature']
            cleaned_tmy = np.column_stack((target_dts,interp_db))   
        cleaned_tmy = np.vstack((column_names,cleaned_tmy))
        if save:
            log.info(('Original TMY data saved to %s'
                     %tmy_file))
            log.info(('Interpolated selected TMY data saved to %s_TMY.csv'
                     %self.location.geocode))
            np.savetxt('%s_TMY.csv'%(self.location.geocode),
                       cleaned_tmy,
                       delimiter=',',
                       fmt='%s', 
                       comments='')
        else:
            #remove unzipped file
            os.remove(tmy_file)
        return tmy_file, cleaned_tmy

if __name__ == "__main__":
    address = 'caffe strada, berkeley'
    test = Location(address)
    print 'address (from user):',address
    print 'address (actual):',test.real_addrs
    print 'lat:',test.lat,' lon:',test.lon
    print 'nearest_geocode:',test.geocode
    start = datetime.datetime(2015,1,1,0,0)
    end = datetime.datetime(2015,1,3,0,0)
    i = 15
    #hist_weather = Weather(start=start, end=end, key=None, 
    #                       geocode=test.geocode, interp_interval=i,
    #                       save=False)
    tmy = TMYData(location=test,
                  year=2015,
                  interp_interval=i,
                  use_dp=False,
                  save=True)
    print 'TMY file:',tmy.tmy_file
    print 'TMY Data:', tmy.cleaned_tmy
