import sys
import os
import gzip
from Bio import SeqIO
import random
import datetime
import argparse


def _argparse():
    parser = argparse.ArgumentParser(description="This is description")
    parser.add_argument('-r1', '--rd1', action='store', dest='read1', required=True, help="input read1 file")
    parser.add_argument('-r2', '--rd2', action='store', dest='read2', help="input read2 file")
    parser.add_argument('-p',  '--prefix', action='store', dest='prefix', required=True, help="this is the output file prefix that you had to give.")
    parser.add_argument('-s',  '--special', action='store', dest='spec_value', type=int, help="Specialized a int number to present the percentage you want, like [10] or [46] etc. which means 10% or 46%.")
    # parser.add_argument('-c',  '--continuous', action='store_true',dest='continuous',default=False,help="a boole value for continuous trim")

    parser.add_argument('-v',  '--version', action='version', version='%(prog)s 0.1')
    return parser.parse_args()


def print_current_time():
    time_stamp = datetime.datetime.now()
    return time_stamp.strftime('%Y.%m.%d-%H:%M:%S')


def get_handle(file):
    if os.path.basename(file).endswith("gz"):
        handle = gzip.open(file, "rU")
    elif os.path.basename(file).endswith(("fq", "fastq")):
        handle = open(file, "rU")
    return handle


def parse_se_fastq(fastq1,phred=33):
    from numpy import fromstring,byte
    while True:
        name1 = fastq1.readline().partition(' ')[0]
        # name2 = fastq2.readline().partition(' ')[0]
        if not name1 :
            break
        read1, nothing1, qual1 = fastq1.readline()[:-1], fastq1.readline(), fastq1.readline()[:-1]
        # read2, nothing2, qual2 = fastq2.readline()[:-1], fastq2.readline(), fastq2.readline()[:-1]
        qual1 = fromstring(qual1,dtype=byte)-phred
        # qual2 = fromstring(qual2,dtype=byte)-phred
        assert name1 == name2, 'fastq1, fastq2 is not paired-end'
        yield name1, read1, qual1

def parse_pe_fastq(fastq1,fastq2,phred=33):
    from numpy import fromstring,byte
    while True:
        name1 = fastq1.readline().partition(' ')[0]
        name2 = fastq2.readline().partition(' ')[0]
        if not name1 or not name2:
            break
        read1, nothing1, qual1 = fastq1.readline()[:-1], fastq1.readline(), fastq1.readline()[:-1]
        read2, nothing2, qual2 = fastq2.readline()[:-1], fastq2.readline(), fastq2.readline()[:-1]
        qual1 = fromstring(qual1,dtype=byte)-phred
        qual2 = fromstring(qual2,dtype=byte)-phred
        assert name1 == name2, 'fastq1, fastq2 is not paired-end'
        yield name1, read1, read2, qual1, qual2

def main():
    '''docstring for main '''
    print("%s all start!\n" % print_current_time())
    parser = _argparse()
    file1 = get_handle(parser.read1)
    num_lines = sum([1 for line in file1])
    file1.close()

    total_reads_number = int(num_lines / 4)
    print("total_reads_number : %s " % total_reads_number)

    file1 = get_handle(parser.read1)
    if parser.read2:
        file2 = get_handle(parser.read2)

    if parser.spec_value:
        number_spec_pct = int(total_reads_number * float(parser.spec_value) / 100)
        print("number spec_value : %s " % number_spec_pct)
        if parser.read2: # PE read
            print("your input is PE read!")
            print("%s : write PE read now." % print_current_time())
            with gzip.open(parser.prefix + "_" + str(parser.spec_value) + "pct_R1.fq.gz", "aw") as f1, gzip.open(parser.prefix + '_' + str(parser.spec_value) + "pct_R2.fq.gz", "aw") as f2:
                index = 1
                for i in parse_pe_fastq(file1,file2):
                    if index <= number_spec_pct:
                        name, seq1, seq2, qual1, qual2 = i
                        f1.write('{name}\n{seq}\n+\n{qual}\n'.format(name=name,seq=seq1,qual=qual1))
                        f2.write('{name}\n{seq}\n+\n{qual}\n'.format(name=name,seq=seq2,qual=qual2))
            print("%s : Finished write PE read" % print_current_time())
        else: # SE 
            print("your input is SE read!")
            print("write SE read now %s"% print_current_time())
            with gzip.open(parser.prefix + "_" + str(parser.spec_value) + "pct_R1.fq.gz", "w") as f1:
                for index, line1 in enumerate(file1, 1):
                    line2 = file1.next()
                    line3 = file1.next()
                    line4 = file1.next()
                    if index <= number_spec_pct:
                        f1.write('{read}\n{seq}\n+\n{qual}\n'.format(read=line1,seq=line2,qual=line4))
            print("%s : finish write SE read." % print_current_time())
    else:
        number_05pct = int(total_reads_number * 0.05)
        number_10pct = int(total_reads_number * 0.1)
        number_20pct = int(total_reads_number * 0.2)
        number_40pct = int(total_reads_number * 0.4)
        number_60pct = int(total_reads_number * 0.6)
        number_80pct = int(total_reads_number * 0.8)

        # print("%s shuffle random list\n" % print_current_time())
        # random.shuffle(read1_li)
        # print("%s finish shuffle random list\n" % print_current_time())
        print("cutting number will be: 5%,10%,20%,40%,60%,80%")
        print("%s writing to fastq...\n" % print_current_time())
        if parser.read2:
            print("%s open gzip out file\n" % print_current_time())
            with gzip.open(parser.prefix + "_05pct_R1.fq.gz", "aw") as f1,  gzip.open(parser.prefix + "_05pct_R2.fq.gz", "aw") as f2,  gzip.open(parser.prefix + "_10pct_R1.fq.gz", "aw") as f3, \
                    gzip.open(parser.prefix + "_10pct_R2.fq.gz", "aw") as f4,  gzip.open(parser.prefix + "_20pct_R1.fq.gz", "aw") as f5,  gzip.open(parser.prefix + "_20pct_R2.fq.gz", "aw") as f6, \
                    gzip.open(parser.prefix + "_40pct_R1.fq.gz", "aw") as f7,  gzip.open(parser.prefix + "_40pct_R2.fq.gz", "aw") as f8,  gzip.open(parser.prefix + "_60pct_R1.fq.gz", "aw") as f9, \
                    gzip.open(parser.prefix + "_60pct_R2.fq.gz", "aw") as f10, gzip.open(parser.prefix + "_80pct_R1.fq.gz", "aw") as f11, gzip.open(parser.prefix + "_80pct_R2.fq.gz", "aw") as f12:
                print("%s finish open gzip outfile \n" % print_current_time())
                print("%s start writing fastq\n" % print_current_time())
                for index, each in enumerate(read1_dict, 1):
                    if index <= number_05pct:
                        SeqIO.write(read1_dict[each], f1, "fastq")
                        SeqIO.write(read2_dict[each], f2, "fastq")
                    if index <= number_10pct:
                        SeqIO.write(read1_dict[each], f3, "fastq")
                        SeqIO.write(read2_dict[each], f4, "fastq")
                    if index <= number_20pct:
                        SeqIO.write(read1_dict[each], f5, "fastq")
                        SeqIO.write(read2_dict[each], f6, "fastq")
                    if index <= number_40pct:
                        SeqIO.write(read1_dict[each], f7, "fastq")
                        SeqIO.write(read2_dict[each], f8, "fastq")
                    if index <= number_60pct:
                        SeqIO.write(read1_dict[each], f9, "fastq")
                        SeqIO.write(read2_dict[each], f10, "fastq")
                    if index <= number_80pct:
                        SeqIO.write(read1_dict[each], f11, "fastq")
                        SeqIO.write(read2_dict[each], f12, "fastq")

        else:
            print("%s open gzip out file\n" % print_current_time())
            with gzip.open(parser.prefix + "_05pct_R1.fq.gz", "aw") as f1,  gzip.open(parser.prefix + "_10pct_R1.fq.gz", "aw") as f3, gzip.open(parser.prefix + "_20pct_R1.fq.gz", "aw") as f5, \
                    gzip.open(parser.prefix + "_40pct_R1.fq.gz", "aw") as f7,  gzip.open(parser.prefix + "_60pct_R1.fq.gz", "aw") as f9, gzip.open(parser.prefix + "_80pct_R1.fq.gz", "aw") as f11:
                print("%s finish open gzip outfile \n" % print_current_time())
                print("%s start writing fastq\n" % print_current_time())
                '''
                for index, each in enumerate(read1_dict, 1):
                    if index <= number_05pct:
                        SeqIO.write(read1_dict[each], f1, "fastq")
                    if index <= number_10pct:
                        SeqIO.write(read1_dict[each], f3, "fastq")
                    if index <= number_20pct:
                        SeqIO.write(read1_dict[each], f5, "fastq")
                    if index <= number_40pct:
                        SeqIO.write(read1_dict[each], f7, "fastq")
                    if index <= number_60pct:
                        SeqIO.write(read1_dict[each], f9, "fastq")
                    if index <= number_80pct:
                        SeqIO.write(read1_dict[each], f11, "fastq")
                '''
                for index, line1 in enumerate(file1, 1):
                    line2 = file1.next()
                    line3 = file1.next()
                    line4 = file1.next()
                    if index <= number_05pct:
                        f1.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
                    if index <= number_10pct:
                        f3.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
                    if index <= number_20pct:
                        f5.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
                    if index <= number_40pct:
                        f7.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
                    if index <= number_60pct:
                        f9.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
                    if index <= number_80pct:
                        f11.write("{read}\n{seq}\n+\n{qual}\n".format({'read':line1,'seq':line2,'qual':line4}))
        print("%s all finished!\n" % print_current_time())
    print("%s all finished!\n" % print_current_time())
if __name__ == '__main__':
    main()
