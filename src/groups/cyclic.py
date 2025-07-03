from lib.simulation import approximate_sigma_mgf, matrix_to_eigenvalues

# I think there is a faster way to find eigenvalues directly in this case


def random_matrix():
    pass


approximate_sigma_mgf(lambda: get_eigenvalues(random_matrix()), 5)
