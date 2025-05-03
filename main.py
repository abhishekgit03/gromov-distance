import matplotlib
matplotlib.use('Agg')

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import scipy.sparse as sps
from scipy.spatial.distance import cdist
from persim import gromov_hausdorff
import os

os.makedirs("images", exist_ok=True)

# Generate Metric Spaces
def generate_circle_points(n_points=20, radius=1):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    return np.stack([radius * np.cos(angles), radius * np.sin(angles)], axis=1)

def generate_noisy_ellipse_points(n_points=20, a=1.5, b=3, noise=0.2):
    angles = np.linspace(0, 2*np.pi, n_points, endpoint=False)
    x = a * np.cos(angles) + np.random.normal(0, noise, n_points)
    y = b * np.sin(angles) + np.random.normal(0, noise, n_points)
    return np.stack([x, y], axis=1)

np.random.seed(42)
X = generate_circle_points()
Y = generate_noisy_ellipse_points()

# Visualize Metric Spaces
plt.figure(figsize=(6,6))
plt.scatter(X[:,0], X[:,1], label='Circle', s=50)
plt.scatter(Y[:,0], Y[:,1], label='Noisy Ellipse', s=50)
plt.title("Metric Spaces: Circle vs Noisy Ellipse")
plt.legend()
plt.grid(True)
plt.axis('equal')
plt.savefig('images/metric_spaces.png')
plt.close()

# Compute Distance Matrices
D_X = cdist(X, X)
D_Y = cdist(Y, Y)

# Visualize Distance Matrices
fig, axs = plt.subplots(1, 2, figsize=(12, 5))
axs[0].imshow(D_X, cmap='viridis')
axs[0].set_title('Distance Matrix: Circle')
fig.colorbar(axs[0].images[0], ax=axs[0])
axs[1].imshow(D_Y, cmap='viridis')
axs[1].set_title('Distance Matrix: Noisy Ellipse')
fig.colorbar(axs[1].images[0], ax=axs[1])
plt.suptitle("Internal Distance Structures")
plt.savefig('images/distance_matrices.png')
plt.close()

# Prepare Adjacency Matrices
D_X_norm = D_X / D_X.max()
D_Y_norm = D_Y / D_Y.max()
threshold = 0.5
A_X = sps.csr_matrix(D_X_norm < threshold)
A_Y = sps.csr_matrix(D_Y_norm < threshold)

# Compute Gromov-Hausdorff Distance
lower_bound, upper_bound = gromov_hausdorff(A_X, A_Y)
print(f"\nGromov-Hausdorff Distance bounds: [{lower_bound:.4f}, {upper_bound:.4f}]\n")

# Basic Approximation
basic_dist = np.max(np.abs(D_X_norm - D_Y_norm)) / 2
print(f"Basic approximation of GH distance: {basic_dist:.4f}")

# Animate Matching
fig, ax = plt.subplots(figsize=(6,6))
def animate(i):
    ax.clear()
    ax.scatter(X[:,0], X[:,1], color='blue', label='Circle')
    ax.scatter(Y[:,0], Y[:,1], color='red', label='Noisy Ellipse')
    for j in range(min(i, len(X))):
        ax.plot([X[j,0], Y[j,0]], [X[j,1], Y[j,1]], 'k--', alpha=0.5)
    ax.legend()
    ax.set_xlim(-3, 3)
    ax.set_ylim(-3, 3)
    ax.set_aspect('equal')
    ax.set_title(f"Matching Frame {i}")

ani = animation.FuncAnimation(fig, animate, frames=len(X)+2, interval=500)
ani.save('images/matching.gif', writer='pillow')
plt.close()
print("Saved matching animation as images/matching.gif")

# Morphing and GH Distance Evolution
def morph(t, Y, X):
    return (1-t)*Y + t*X

gh_distances = []
basic_distances = []
ts = np.linspace(0, 1, 30)

for t in ts:
    morphed = morph(t, Y, X)
    D_morphed = cdist(morphed, morphed)
    D_morphed_norm = D_morphed / D_morphed.max()
    A_morphed = sps.csr_matrix(D_morphed_norm < threshold)
    lb, ub = gromov_hausdorff(A_X, A_morphed)
    gh_distances.append(ub)
    basic = np.max(np.abs(D_X_norm - D_morphed_norm)) / 2
    basic_distances.append(basic)

# Plot GH Distance Evolution
plt.figure(figsize=(10,6))
plt.plot(ts, gh_distances, marker='o', label='GH Distance (Upper Bound)')
plt.plot(ts, basic_distances, marker='x', linestyle='--', label='Basic Distance Approximation')
plt.xlabel("Morphing Progress (t)")
plt.ylabel("Distance")
plt.title("Evolution of Gromov–Hausdorff Distance during Morphing")
plt.legend()
plt.grid(True)
plt.savefig('images/gh_evolution.png')
plt.close()

# Morphing Snapshots
fig, axes = plt.subplots(2, 3, figsize=(15, 10))
axes = axes.flatten()
sample_ts = [0, 0.2, 0.4, 0.6, 0.8, 1.0]
for i, t in enumerate(sample_ts):
    morphed = morph(t, Y, X)
    axes[i].scatter(morphed[:,0], morphed[:,1], color='purple')
    axes[i].set_title(f"t = {t:.1f}")
    axes[i].set_xlim(-3, 3)
    axes[i].set_ylim(-3, 3)
    axes[i].set_aspect('equal')
    axes[i].grid(True)

plt.tight_layout()
plt.savefig('images/morphing_sequence.png')
plt.close()

