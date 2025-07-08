"""
A file with various helpers for running simulations
"""

from sage.all import *


def matrix_to_eigenvalues(M):
    return [l.n() for l in M.eigenvalues()]


def approximate_sigma_mgf(
    generate_X,  # A function that when called, produces a random list of eigenvalues
    num_eigenvalues,  # The expected number of eigenvalues (including multiplicities)
    partition_size,  # partitions up to this size will be included in calculations
    stopping_std,  # Approximate standard deviation of the output variables which is acceptable
    min_num_samples=10,  # We won't stop if less then this number of samples have been considered
    max_num_samples=100,  # We don't want to compute this forever, so abort if taking too long. If none, don't stop
    print_extra_info=True,
):
    # Idea: use a simple Monte Carlo method; also find empirical variance of data and
    # use it and CLT to estimate the variance of the entries
    # For each permutation \tau corresponding to m_\tau of size at most `partition_size`,
    # we estimate \mathbb{E}[X_{h_\tau}]

    assert min_num_samples > 1, "Have to use at least 2 samples"

    Sym = SymmetricFunctions(ZZ)
    h = Sym.complete()

    num_samples = 0

    X = generate_X()
    all_partitions_and_polys = []
    for i in range(1, partition_size + 1):
        for partition in Partitions(i):
            all_partitions_and_polys.append(
                (partition, h(partition).expand(num_eigenvalues))
            )

    sums_of_coefficients = {
        p: CDF(0) for p, _ in all_partitions_and_polys
    }  # For \mathbb{E}[X_{h_\tau}]
    sums_of_abs_squares_of_coefficients = {
        p: CDF(0) for p, _ in all_partitions_and_polys
    }  # For Var[X_{h_\tau}

    def get_sample_variance(partition):
        return (
            sums_of_abs_squares_of_coefficients[partition]
            - (abs(sums_of_coefficients[partition]) ** 2) / (num_samples)
        ) / (num_samples - 1)

    sample_index = 1
    while True:

        # Notify about progress every 100 samples
        should_print_extra_info = (
            sample_index % 100 == 0
        ) and print_extra_info
        if should_print_extra_info:
            if max_num_samples is not None:
                print(f"Processing sample {sample_index}/{max_num_samples}")
            else:
                print(f"Processing sample {sample_index}")

        X = generate_X()
        assert (
            len(X) == num_eigenvalues
        ), f"The multiset of eigenvalues should have size {num_eigenvalues}, not {len(X)}"

        max_variance = 0
        num_samples += 1

        # Don't check stopping condition if aren't allowed to stop yet
        if num_samples <= min_num_samples:
            all_samples_have_low_enough_variance = False
        else:
            all_samples_have_low_enough_variance = True

        for partition, poly in all_partitions_and_polys:
            coefficient = CDF(poly(*X))

            sums_of_coefficients[partition] += coefficient
            sums_of_abs_squares_of_coefficients[partition] += abs(
                coefficient**2
            )

            # If we already know that this isn't accurate enough, no need to recalculate variances
            if not all_samples_have_low_enough_variance:
                continue

            sample_variance = get_sample_variance(partition)
            if should_print_extra_info:
                print(
                    f"Sample variance for {partition} is {sample_variance}; estimate variance is {(sample_variance / sqrt(num_samples)).n()}"
                )
            # Apply CLT to estimate variance of this specific entry
            if sample_variance > sqrt(num_samples) * stopping_std**2:
                all_samples_have_low_enough_variance = False

        sample_index += 1
        if all_samples_have_low_enough_variance or (
            max_num_samples is not None and sample_index > max_num_samples
        ):
            break

    # After the loop
    expectations = {
        p: sums_of_coefficients[p] / num_samples
        for p, _ in all_partitions_and_polys
    }
    estimation_stds = {
        p: (sqrt(get_sample_variance(p) / sqrt(num_samples))).n()
        for p, _ in all_partitions_and_polys
    }
    sample_stds = {
        p: sqrt(get_sample_variance(p)).n()
        for p, _ in all_partitions_and_polys
    }
    return expectations, estimation_stds, sample_stds
