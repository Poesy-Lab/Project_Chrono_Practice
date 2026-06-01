from generate_data_visualization_components import render_visualization_components


if __name__ == "__main__":
    paths = render_visualization_components()
    if len(paths) != 1:
        raise RuntimeError(f"Expected one sensor component PNG, got {len(paths)} outputs")
    print(paths[0])
