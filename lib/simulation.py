"""
A file with various helpers for running simulations
"""

from sage.all import *


def matrix_to_eigenvalues(M):
    return [l.n() for l in M.eigenvalues()]


def approximate_sigma_mgf(
    generate_X,
    order,
    stopping_std,  # Approximate standard deviation of the output variables which is acceptable
    min_num_samples=10,  # We won't stop if less then this number of samples have been considered
):
    # Idea: use a simple Monte Carlo method; also find empirical variance of data and
    # use it and CLT to estimate the variance of the entries
    # For each permutation \tau corresponding to m_\tau of order at most `order`,
    # we estimate \mathbb{E}[X_{h_\tau}]

    assert min_num_samples > 1, "Have to use at least 2 samples"

    Sym = SymmetricFunctions(ZZ)
    h = Sym.complete()

    sums_of_coefficients = {
        p: CDF(0) for p in Partitions(order)
    }  # For \mathbb{E}[X_{h_\tau}]
    sums_of_abs_squares_of_coefficients = {
        p: CDF(0) for p in Partitions(order)
    }  # For Var[X_{h_\tau}

    num_samples = 0

    def get_sample_variance(partition):
        return (
            sums_of_abs_squares_of_coefficients[partition]
            - (abs(sums_of_coefficients[partition]) ** 2) / (num_samples)
        ) / (num_samples - 1)

    while True:
        X = generate_X()

        max_variance = 0
        num_samples += 1

        # Don't check stopping condition if aren't allowed to stop yet
        if num_samples <= min_num_samples:
            all_samples_have_low_enough_variance = False
        else:
            all_samples_have_low_enough_variance = True

        for partition in Partitions(order):
            coefficient = h(partition).expand(len(X))(*X)

            coefficient = CDF(coefficient)

            sums_of_coefficients[partition] += coefficient
            sums_of_abs_squares_of_coefficients[partition] += abs(
                coefficient**2
            )

            # If we already know that this isn't accurate enough, no need to recalculate variances
            if not all_samples_have_low_enough_variance:
                continue

            sample_variance = get_sample_variance(partition)
            # Apply CLT to estimate variance of this specific entry
            if sample_variance > sqrt(num_samples) * stopping_std**2:
                all_samples_have_low_enough_variance = False

        if all_samples_have_low_enough_variance:
            expectations = {
                p: sums_of_coefficients[p] / num_samples
                for p in Partitions(order)
            }
            stds = {
                p: (
                    sqrt(get_sample_variance(partition) / sqrt(num_samples))
                ).n()
                for p in Partitions(order)
            }
            return expectations, stds
