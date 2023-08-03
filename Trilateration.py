from scipy.optimize import least_squares

# Least square algorithm for 2D indoor positioning
def trilaterate(distances, positions):
  def residuals(x, distances, positions):
    residuals = []
    for i in range(len(distances)):
      residuals.append(np.linalg.norm(x - positions[i]) - distances[i])
    return residuals
  
  initial_guess = np.mean(positions, axis=0)
  result = least_squares(residuals, initial_guess, args=(distances, positions))
  return result.x

# 2D trilateration algorithm 
def trilateration_2d_co(distances, positions, name):
    # Calculate the position of the object
    position = trilaterate(distances, positions)
    
    final = [name, position[0], position[1]]
    return final

# 3D trilateration algorithm
def trilateration_3d_co(distances, positions, name):
    # Calculate the position of the object
    position = trilaterate(distances, positions)

    final = [name, position[0], position[1], position[2]]
    return final