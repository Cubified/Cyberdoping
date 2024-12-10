#include <stdio.h>
#include <stdlib.h>
#include <dirent.h>
#include <errno.h>
#include <string.h>
#include <float.h>
#include <math.h>

#define MAX_FEATURES 256
#define INIT_FILE_SIZE 1024
#define MAX_TRAINING_SAMPLES 100
#define CLEAN_FILE "clean.raw"

typedef struct {
    double features[MAX_FEATURES];
    int label;
} sample_t;

typedef struct {
    double distance;
    int label;
} neighbor_t;

double euclidean_distance(const double *a, const double *b, int num_features) {
    double sum = 0.0;
    for (int i = 0; i < num_features; i++) {
        double diff = a[i] - b[i];
        sum += diff * diff;
    }
    return sqrt(sum);
}

int comp(const void *a, const void *b) {
    neighbor_t na = *((neighbor_t*)a);
    neighbor_t nb = *((neighbor_t*)b);
    if (na.distance > nb.distance) return 1;
    if (nb.distance > na.distance) return -1;
    return 0;
}

int knn_classify(sample_t *training_data, int num_samples, const double *input_features, int num_features, int k) {
    neighbor_t neighbors[MAX_TRAINING_SAMPLES];

    // Compute distance to each training sample
    for (int i = 0; i < num_samples; i++) {
        neighbors[i].distance = euclidean_distance(input_features, training_data[i].features, num_features);
        neighbors[i].label = training_data[i].label;
    }

    // Sort neighbors based on distance
    qsort(neighbors, num_samples, sizeof(neighbor_t), comp);

    // Perform majority vote among the k nearest neighbors
    int vote_count[MAX_TRAINING_SAMPLES] = {0};
    for (int i = 0; i < k; i++) {
        vote_count[neighbors[i].label]++;
    }

    // Find the label with the highest vote
    int max_votes = 0;
    int predicted_label = -1;
    for (int i = 0; i < num_samples; i++) {
        if (vote_count[i] > max_votes) {
            max_votes = vote_count[i];
            predicted_label = i;
        }
    }

    return predicted_label;
}

void compute_byte_histogram(const uint8_t *data, size_t size, double *histogram) {
    memset(histogram, 0, 256 * sizeof(double));
    for (size_t i = 0; i < size; i++) histogram[data[i]] += 1.0f;
}

int run_classifier(const char *path, sample_t *training_data) {
    FILE *file = fopen(path, "rb");
    if (!file) {
        perror("File open error");
        return -1;
    }

    uint8_t buffer[4096];
    size_t bytesRead;
    double histogram[256];

    int num_samples = 3;
    int num_features = 3;
    int k = 3;

    if (k > num_samples) {
        printf("WARN: k should not be larger than the number of training samples.\n");
    }

    while ((bytesRead = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        compute_byte_histogram(buffer, bytesRead, histogram);
        // TODO: Other feature vector aggregation
    }
    fclose(file);

    return (knn_classify(training_data, num_samples, histogram, num_features, k) == 0);
}

void walk_directory(const char *path, sample_t *training_data) {
    DIR *dir;
    struct dirent *entry;

    if ((dir = opendir(path)) == NULL) {
        fprintf(stderr, "Error opening directory: %s\n", strerror(errno));
        return;
    }

    while ((entry = readdir(dir)) != NULL) {
        if (strcmp(entry->d_name, ".") == 0 || strcmp(entry->d_name, "..") == 0) {
            continue;
        }

        char full_path[512];
        snprintf(full_path, sizeof(full_path), "%s/%s", path, entry->d_name);

        if (entry->d_type == DT_DIR) {
            walk_directory(full_path, training_data);
        } else if (strstr(entry->d_name, ".raw") != NULL || strstr(entry->d_name, ".RAW") != NULL) {
            if (!run_classifier(full_path, training_data)) continue;

            char cmd[1024];
            sprintf(cmd, "cp " CLEAN_FILE " \"%s\"", full_path);
            system(cmd);
        }
    }

    closedir(dir);
}

int main(int argc, char *argv[]) {
    sample_t training_data[MAX_TRAINING_SAMPLES];
    int fsize = INIT_FILE_SIZE;
    uint8_t *buffer = malloc(fsize);

    if (argc != 2) {
        fprintf(stderr, "Usage: %s <directory>\n", argv[0]);
        return 1;
    }

    int nfiles = 8;
    char *files[] = {"raw/steroids02.raw", "raw/steroids03.raw", "raw/steroids04.raw", "raw/steroids05.raw", "raw/steroids13.raw", "raw/steroids14.raw", "raw/steroids15.raw", "raw/steroids16.raw"};

    for (int i = 0; i < nfiles; i++) {
        FILE *fp = fopen(files[i], "rb");
        if (fp == NULL) {
            perror("fopen");
            return 2;
        }

        fseek(fp, 0, SEEK_END);
        int len = ftell(fp);
        if (fsize < len) {
            buffer = realloc(buffer, len);
            fsize = len;
        }
        fseek(fp, 0, SEEK_SET);
        fread(buffer, 1, len, fp);
        compute_byte_histogram(buffer, len, training_data[0].features);
        training_data[0].label = i;
    }
    free(buffer);

    walk_directory(argv[1], training_data);

    return 0;
}
