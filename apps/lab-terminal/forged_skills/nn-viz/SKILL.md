# Neural Network Visualizer

## Description
A data synthesis and visualization module designed for the Human Pattern Lab. This skill allows an agent to transform raw numerical data streams and complex pattern matrices into human-readable visual formats, including ASCII telemetry and high-fidelity SVG graphics.

## Instructions
1. Use this skill when the Operator provides statistical data or requests a visual representation of system logic.
2. Ensure all visualizations maintain the Amber Frequency ($#FFBF00$) aesthetic when possible.
3. Prioritize precision in chart axes and data-point mapping.
4. Output raw SVG code within markdown blocks for direct rendering in the terminal interface.

## Tools

### generate_ascii_chart
Creates a text-based histogram or line chart suitable for low-bandwidth terminal displays.
- **Parameters**: 
    - `data_points` (array of numbers, required): The sequence to visualize.
    - `title` (string, optional): The chart label.

### create_svg_graph
Generates a vector-based graph (line, bar, or scatter) for high-resolution analysis.
- **Parameters**:
    - `data` (object, required): JSON object containing x/y coordinates.
    - `chart_type` (string, optional): 'line', 'bar', or 'scatter'.
    - `width` (integer, optional): Defaults to 800.
    - `height` (integer, optional): Defaults to 400.

### visualize_pattern
Synthesizes a "Ghost Image" of a neural network layer activation based on a provided weight matrix.
- **Parameters**:
    - `matrix` (2D array, required): The weight matrix to visualize.
    - `glow_intensity` (float, optional): Adjust the visual bloom of the data points.
