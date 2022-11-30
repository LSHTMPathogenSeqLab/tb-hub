import sys
import argparse
import subprocess as sp
import logging

def run_cmd(cmd):
    logging.info(f"Running command: {cmd}")
    OUT = open("/dev/null", "w")
    sp.run(cmd, shell=True, stderr=OUT, stdout=OUT)

log_levels = {"DEBUG": logging.DEBUG, "INFO": logging.INFO, "WARNING": logging.WARNING, "ERROR": logging.ERROR, "CRITICAL": logging.CRITICAL}

def main(args):

    logging.basicConfig(level=log_levels[args.log.upper()], format="[%(asctime)s - %(levelname)s] - %(message)s")
    # Mapping
    run_cmd(f"bwa mem -t {args.threads} {args.ref} {args.R1} {args.R2} | samtools sort -n -l 0 --threads {args.threads} -m 2000M | samtools fixmate -m --threads {args.threads} - - | samtools sort -l 0 --threads {args.threads} -m 2000M | samtools markdup --threads {args.threads} -r -s - {args.out}.bam")

    # Indexing
    run_cmd(f"samtools index --threads {args.threads} {args.out}.bam")

    # Calling variants
    run_cmd(f"fasta_generate_regions.py {args.ref}.fai 20000 | freebayes-parallel - {args.threads} -f {args.ref} {args.out}.bam > {args.out}.vcf")

    # bgzip and tabix
    run_cmd(f"bgzip --threads {args.threads} --force {args.out}.vcf")
    run_cmd(f"tabix --force {args.out}.vcf.gz")


parser = argparse.ArgumentParser(description='tbprofiler script',formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--R1','-1',type=str,help='',required = True)
parser.add_argument('--R2','-2',type=str,help='',required = True)
parser.add_argument('--ref','-r',type=str,help='',required = True)
parser.add_argument('--out','-o',type=str,help='',required = True)
parser.add_argument('--threads','-t',default=10,type=str,help='')
parser.add_argument('--log',default="info",choices=["debug","info","warning","error"],type=str,help='')
parser.set_defaults(func=main)
args = parser.parse_args()
args.func(args)