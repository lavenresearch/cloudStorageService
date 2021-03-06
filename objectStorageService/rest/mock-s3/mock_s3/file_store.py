#coding=utf-8
import ConfigParser
import md5
import os
import shutil
from datetime import datetime
import random
from errors import BucketNotEmpty, NoSuchBucket
from models import Bucket, BucketQuery, S3Item


CONTENT_FILE = '.mocks3_content'
METADATA_FILE = '.mocks3_metadata'


class FileStore(object):
    def __init__(self, root):
        self.root = root
        self.max_copy=3
        self.max_strip=3
        if not os.path.exists(self.root):
            os.makedirs(self.root)
        self.buckets = self.get_all_buckets()

    def get_bucket_folder(self, bucket_name):
        return os.path.join(self.root, bucket_name)

    def get_all_buckets(self):
        buckets = []
        bucket_list = os.listdir(self.root)
        bucket_list.sort()
        for bucket in bucket_list:
            mtime = os.stat(os.path.join(self.root, bucket)).st_mtime#获得修改时间
            create_date = datetime.fromtimestamp(mtime).strftime('%Y-%m-%dT%H:%M:%S.000Z')
            buckets.append(Bucket(bucket, create_date))
        return buckets

    def get_bucket(self, bucket_name):
        for bucket in self.buckets:
            if bucket.name == bucket_name:
                return bucket
        return None

    def create_bucket(self, bucket_name):
        if bucket_name not in [bucket.name for bucket in self.buckets]:
            try:
                os.makedirs(os.path.join(self.root, bucket_name))
            except:
                # mismatch
                pass
            self.buckets = self.get_all_buckets()
        return self.get_bucket(bucket_name)

    def delete_bucket(self, bucket_name):
        bucket = self.get_bucket(bucket_name)
        if not bucket:
            raise NoSuchBucket
        try:
            os.rmdir(os.path.join(self.root, bucket_name))
            self.buckets = self.get_all_buckets()
        except:
            # TODO: for now assume exception is directory is not empty
            raise BucketNotEmpty

    def get_all_keys(self, bucket, **kwargs):
        max_keys = int(kwargs['max_keys'])
        is_truncated = False
        matches = []
        for root, dirs, files in os.walk(os.path.join(self.root, bucket.name)):
            pattern = os.path.join(self.root, bucket.name, kwargs['prefix'])
            if root.startswith(pattern) and METADATA_FILE in files:
                config = ConfigParser.RawConfigParser()
                files_parsed = config.read(os.path.join(root, METADATA_FILE))
                metadata = {}
                if files_parsed:
                    metadata['size'] = config.getint('metadata', 'size')
                    metadata['md5'] = config.get('metadata', 'md5')
                    metadata['content_type'] = config.get('metadata', 'content_type')
                    metadata['creation_date'] = config.get('metadata', 'creation_date')
                    metadata['filename']=config.get('metadata','filename')
                    metadata['strip_num']=config.getint('metadata','strip_num')
                    metadata['copy_num']=config.getint('metadata','copy_num')
                    if config.has_option('metadata', 'modified_date'):
                        metadata['modified_date'] = config.get('metadata', 'modified_date')

                actual_key = root.replace(self.root, '')
                actual_key = actual_key.replace('/' + bucket.name + '/', '')
                matches.append(S3Item(actual_key, **metadata))
                if len(matches) >= max_keys:
                    is_truncated = True
                    break
        return BucketQuery(bucket, matches, is_truncated, **kwargs)

    def get_item(self, bucket_name, item_name):
        key_name = os.path.join(bucket_name, item_name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            if config.has_option('metadata', 'modified_date'):
                metadata['modified_date'] = config.get('metadata', 'modified_date')
            metadata['strip_num']=config.getint('metadata','strip_num')
            metadata['copy_num']=config.getint('metadata','copy_num')

        if not metadata:
            return None
        #file_copy=random.randint(0,2)

        item = S3Item(key_name, **metadata)
        #item.io = open(filename, 'rb')
        
        return item

    '''
    def copy_item(self, src_bucket_name, src_name, bucket_name, name, handler):
        src_key_name = os.path.join(src_bucket_name, src_name)
        src_dirname = os.path.join(self.root, src_key_name)
        src_filename = os.path.join(src_dirname, CONTENT_FILE)
        src_metafile = os.path.join(src_dirname, METADATA_FILE)

        bucket = self.get_bucket(bucket_name)
        key_name = os.path.join(bucket.name, name)
        dirname = os.path.join(self.root, key_name)
        filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)

        if not os.path.exists(dirname):
            os.makedirs(dirname)
        shutil.copy(src_filename, filename)
        shutil.copy(src_metafile, metafile)

        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        metadata = {}
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            if config.has_option('metadata', 'modified_date'):
                metadata['modified_date'] = config.get('metadata', 'modified_date')

        return S3Item(key_name, **metadata)
    def store_data(self, bucket, item_name, headers, data,copy_num=1,strip_num=1):
        filename_matrix=[[],[],[]]
        for strip in range(0,self.max_strip):
            for copy in range(0,self.max_copy):
                filename_matrix[strip].append(CONTENT_FILE+'_'+str(strip)+'_'+str(copy))

        key_name = os.path.join(bucket.name, item_name)
        dirname = os.path.join(self.root, key_name)
        #filename = os.path.join(dirname, CONTENT_FILE)
        metafile = os.path.join(dirname, METADATA_FILE)
        
        filename = [[],[],[]]
        for strip in range(0,self.max_strip):
            for copy in range(0,self.max_copy):
                filename[strip].append(os.path.join(dirname,filename_matrix[strip][copy]))

        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            metadata['strip_num']=config.getint('metadata','strip_num')
            metadata['copy_num']=config.getint('metadata','copy_num')

        m = md5.new()

        lower_headers = {}
        for key in headers:
            lower_headers[key.lower()] = headers[key]
        headers = lower_headers
        if 'content-type' not in headers:
            headers['content-type'] = 'application/octet-stream'

        size = int(headers['content-length'])
        
        m.update(data)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
        with open(filename, 'wb') as f:
            f.write(data)

        if metadata:
            metadata['md5'] = m.hexdigest()
            metadata['modified_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            metadata['content_type'] = headers['content-type']
            metadata['size'] = size
        else:
            metadata = {
                'content_type': headers['content-type'],
                'creation_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'md5': m.hexdigest(),
                'filename': filename,
                'size': size,
            }
        config.add_section('metadata')
        config.set('metadata', 'size', metadata['size'])
        config.set('metadata', 'md5', metadata['md5'])
        config.set('metadata', 'filename', metadata['filename'])
        config.set('metadata', 'content_type', metadata['content_type'])
        config.set('metadata', 'creation_date', metadata['creation_date'])
        if 'modified_date' in metadata:
            config.set('metadata', 'modified_date', metadata['modified_date'])
        with open(metafile, 'wb') as configfile:
            config.write(configfile)

        s3_item = S3Item(key, **metadata)
        s3_item.io = open(filename, 'rb')
        return s3_item
    '''
    def store_item(self, bucket, item_name, handler,copy_num=1,strip_num=1):
        filename_matrix=[[],[],[]] 
        for strip in range(0,self.max_strip):
            for copy in range(0,self.max_copy):
                filename_matrix[strip].append(CONTENT_FILE+'_'+str(strip)+'_'+str(copy))
        key_name = os.path.join(bucket.name, item_name)
        dirname = os.path.join(self.root, key_name)
        metafile = os.path.join(dirname, METADATA_FILE)
       
        #filename = os.path.join(dirname, CONTENT_FILE)
        filename = [[],[],[]]
        
        for strip in range(0,self.max_strip):
            for copy in range(0,self.max_copy):
                filename[strip].append(os.path.join(dirname,filename_matrix[strip][copy]))
        #deal with the boundary
        boundary = handler.headers.plisttext.split("=")[1]
        print 'size boundary',len(boundary)
        fullsize = int(handler.headers['content-length'])
        remainbytes=fullsize

        line=handler.rfile.readline()
        remainbytes -=len(line)

        line=handler.rfile.readline()
        remainbytes -=len(line)

        line=handler.rfile.readline()
        remainbytes -=len(line)

        line=handler.rfile.readline()
        print 'line 4',len(line)
        remainbytes -=len(line)
        
        remainbytes -=(len(boundary)+8)
        size=remainbytes
        #print filename1
        metadata = {}
        config = ConfigParser.RawConfigParser()
        files_parsed = config.read(metafile)
        if files_parsed:
            metadata['size'] = config.getint('metadata', 'size')
            metadata['md5'] = config.get('metadata', 'md5')
            metadata['filename'] = config.get('metadata', 'filename')
            metadata['content_type'] = config.get('metadata', 'content_type')
            metadata['creation_date'] = config.get('metadata', 'creation_date')
            metadata['strip_num']=config.getint('metadata','strip_num')
            metadata['copy_num']=config.getint('metadata','copy_num')
        m = md5.new()

        headers = {}
        for key in handler.headers:
            headers[key.lower()] = handler.headers[key]
        if 'content-type' not in headers:
            headers['content-type'] = 'application/octet-stream'

        strip_size=size/strip_num

        parse_size=1024*1024*10     #10M
        #idata = handler.rfile.read(size)
        if not os.path.exists(dirname):
            os.makedirs(dirname)

        temp_size=strip_size
         
        for strip in range(0,strip_num):
            strip_recv_size=0
            with open(filename[strip][0], 'wb') as f:
                if strip==(strip_num-1):
                    temp_size=size-strip_size*(strip_num-1)
                while strip_recv_size<temp_size:
                    r_size=min(parse_size,temp_size-strip_recv_size)
                    data=handler.rfile.read(r_size)
                    strip_recv_size+=r_size
                    m.update(data)
                    f.write(data)

            for copy in range(1,copy_num):
                shutil.copyfile(filename[strip][0],filename[strip][copy])

        end_boundary=handler.rfile.read(len(boundary)+6)
        #print end_boundary.strip()
        #if end_boundary.strip() == boundary+'__':
        #    print 'OK'
        if metadata:
            metadata['md5'] = m.hexdigest()
            metadata['modified_date'] = datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z')
            metadata['content_type'] = headers['content-type'].split(';')[0]
            metadata['size'] = size
            metadata['strip_num']=strip_num
            metadata['copy_num']=copy_num
        else:
            metadata = {
                'content_type': headers['content-type'].split(';')[0],
                'creation_date': datetime.now().strftime('%Y-%m-%dT%H:%M:%S.000Z'),
                'md5': m.hexdigest(),
                'filename': os.path.join(dirname, CONTENT_FILE),
                'size': size,
                'strip_num':strip_num,
                'copy_num':copy_num,
            }
        if not config.has_section('metadata'):
            config.add_section('metadata')

        config.set('metadata', 'size', metadata['size'])
        config.set('metadata', 'md5', metadata['md5'])
        config.set('metadata', 'filename', metadata['filename'])
        config.set('metadata', 'strip_num', metadata['strip_num'])
        config.set('metadata', 'copy_num', metadata['copy_num'])
        config.set('metadata', 'content_type', metadata['content_type'])
        config.set('metadata', 'creation_date', metadata['creation_date'])
        if 'modified_date' in metadata:
            config.set('metadata', 'modified_date', metadata['modified_date'])
        with open(metafile, 'wb') as configfile:
            config.write(configfile)
        return S3Item(key, **metadata)

    def delete_item(self, bucket, item_name):
        key_name = os.path.join(bucket.name, item_name)
        dirname = os.path.join(self.root, key_name)
        #os.remove(os.path.join(dirname, METADATA_FILE))
        #filename = os.path.join(dirname, CONTENT_FILE)
        shutil.rmtree(dirname)
