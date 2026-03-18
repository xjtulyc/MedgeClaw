#!/usr/bin/env python3
"""Generate a realistic synthetic VCF with multi-population samples.

Creates a demo dataset for the Equity Scorer with:
- 50 samples across 5 superpopulations (AFR, AMR, EAS, EUR, SAS)
- 200 biallelic SNPs on chr22 with population-differentiated allele frequencies
- Realistic LD-free genotypes drawn from population-specific AFs
- A companion population_map.csv

The allele frequencies are inspired by real 1000 Genomes patterns:
- AFR has highest diversity (highest Het)
- EUR and EAS show founder-effect reduced diversity
- AMR and SAS intermediate

Usage:
    python generate_demo_vcf.py
"""

import csv
import random
from pathlib import Path

random.seed(42)  # reproducible demo

OUTPUT_DIR = Path(__file__).resolve().parent

# ---------------------------------------------------------------------------
# Population design
# ---------------------------------------------------------------------------

POPULATIONS = {
    "AFR": {"n": 8, "label": "African", "countries": ["Nigeria", "Kenya", "Ghana", "South Africa"]},
    "AMR": {"n": 5, "label": "Admixed American", "countries": ["Mexico", "Colombia", "Peru", "Brazil"]},
    "EAS": {"n": 7, "label": "East Asian", "countries": ["China", "Japan", "Korea", "Vietnam"]},
    "EUR": {"n": 22, "label": "European", "countries": ["UK", "Germany", "France", "Spain", "Italy", "Sweden", "Poland", "Ireland"]},
    "SAS": {"n": 8, "label": "South Asian", "countries": ["India", "Pakistan", "Bangladesh", "Sri Lanka"]},
}

N_SNPS = 500
CHROM = "22"
START_POS = 16_000_000


def generate_population_afs(n_snps: int) -> dict:
    """Generate population-specific allele frequencies for each SNP.

    Models three SNP classes:
    1. Common shared (60%): similar AF across populations (global polymorphisms)
    2. Population-differentiated (30%): substantial AF differences (drives FST)
    3. Population-private (10%): high AF in one pop, near-zero elsewhere
    """
    afs = {pop: [] for pop in POPULATIONS}

    for i in range(n_snps):
        r = random.random()

        if r < 0.40:
            # Common shared: base AF 0.1-0.5, moderate per-pop jitter
            base = random.uniform(0.10, 0.50)
            for pop in POPULATIONS:
                jitter = random.gauss(0, 0.08)
                af = max(0.01, min(0.99, base + jitter))
                afs[pop].append(af)

        elif r < 0.85:
            # Population-differentiated: large AF differences (drives FST + PCA)
            # Model realistic out-of-Africa divergence pattern
            afr_af = random.uniform(0.15, 0.75)
            for pop in POPULATIONS:
                if pop == "AFR":
                    afs[pop].append(afr_af)
                elif pop == "EUR":
                    drift = random.uniform(-0.35, -0.05)
                    afs[pop].append(max(0.01, min(0.99, afr_af + drift)))
                elif pop == "EAS":
                    drift = random.uniform(-0.40, -0.10)
                    afs[pop].append(max(0.01, min(0.99, afr_af + drift)))
                elif pop == "SAS":
                    drift = random.uniform(-0.25, 0.05)
                    afs[pop].append(max(0.01, min(0.99, afr_af + drift)))
                elif pop == "AMR":
                    # Admixed: ~40% Indigenous + ~35% EUR + ~25% AFR
                    eur_af = max(0.01, min(0.99, afr_af + random.uniform(-0.35, -0.05)))
                    indigenous = random.uniform(0.05, 0.60)
                    admix = 0.25 * afr_af + 0.35 * eur_af + 0.40 * indigenous
                    afs[pop].append(max(0.01, min(0.99, admix)))

        else:
            # Population-private: high in one pop, near-zero elsewhere
            focal_pop = random.choice(list(POPULATIONS.keys()))
            for pop in POPULATIONS:
                if pop == focal_pop:
                    afs[pop].append(random.uniform(0.20, 0.55))
                else:
                    afs[pop].append(random.uniform(0.00, 0.02))

    return afs


def draw_genotype(af: float) -> str:
    """Draw a diploid genotype from Hardy-Weinberg given allele frequency."""
    r = random.random()
    p = 1 - af  # ref allele freq
    q = af       # alt allele freq
    if r < p * p:
        return "0/0"
    elif r < p * p + 2 * p * q:
        return "0/1"
    else:
        return "1/1"


def generate_samples() -> list:
    """Generate sample IDs with population prefixes."""
    samples = []
    for pop, info in POPULATIONS.items():
        for i in range(info["n"]):
            samples.append(f"{pop}_{i+1:03d}")
    return samples


def write_vcf(samples: list, afs: dict, output_path: Path) -> None:
    """Write the VCF file."""
    with open(output_path, "w") as f:
        # Header
        f.write("##fileformat=VCFv4.3\n")
        f.write("##source=OpenClawBio_DemoGenerator\n")
        f.write(f"##contig=<ID={CHROM},length=51304566>\n")
        f.write('##FORMAT=<ID=GT,Number=1,Type=String,Description="Genotype">\n')
        f.write('##INFO=<ID=AC,Number=A,Type=Integer,Description="Allele count">\n')
        f.write('##INFO=<ID=AN,Number=1,Type=Integer,Description="Total alleles">\n')

        # Column header
        cols = ["#CHROM", "POS", "ID", "REF", "ALT", "QUAL", "FILTER", "INFO", "FORMAT"]
        cols.extend(samples)
        f.write("\t".join(cols) + "\n")

        # Variants
        refs = list("ACGT")
        for snp_idx in range(N_SNPS):
            pos = START_POS + snp_idx * 500  # 500bp spacing
            ref = random.choice(refs)
            alt_choices = [b for b in refs if b != ref]
            alt = random.choice(alt_choices)
            snp_id = f"rs_demo_{snp_idx+1:04d}"

            # Draw genotypes per sample
            genotypes = []
            ac = 0
            an = 0
            for sample in samples:
                pop = sample.split("_")[0]
                af = afs[pop][snp_idx]
                gt = draw_genotype(af)
                genotypes.append(gt)
                alleles = gt.split("/")
                ac += alleles.count("1")
                an += 2

            info = f"AC={ac};AN={an}"
            row = [CHROM, str(pos), snp_id, ref, alt, ".", "PASS", info, "GT"]
            row.extend(genotypes)
            f.write("\t".join(row) + "\n")


def write_population_map(samples: list, output_path: Path) -> None:
    """Write the population map CSV."""
    with open(output_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["sample_id", "population", "superpopulation", "country"])
        for sample in samples:
            pop = sample.split("_")[0]
            info = POPULATIONS[pop]
            country = random.choice(info["countries"])
            writer.writerow([sample, pop, info["label"], country])


def main() -> None:
    print("Generating demo VCF dataset...")
    pop_summary = ", ".join(f"{k} (n={v['n']})" for k, v in POPULATIONS.items())
    print(f"  Populations: {pop_summary}")
    print(f"  Total samples: {sum(v['n'] for v in POPULATIONS.values())}")
    print(f"  SNPs: {N_SNPS}")

    afs = generate_population_afs(N_SNPS)
    samples = generate_samples()

    vcf_path = OUTPUT_DIR / "demo_populations.vcf"
    write_vcf(samples, afs, vcf_path)
    print(f"  VCF: {vcf_path}")

    pop_map_path = OUTPUT_DIR / "demo_population_map.csv"
    write_population_map(samples, pop_map_path)
    print(f"  Population map: {pop_map_path}")

    print("Done.")


if __name__ == "__main__":
    main()
