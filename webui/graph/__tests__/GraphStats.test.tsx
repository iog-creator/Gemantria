import { render, screen } from "@testing-library/react";
import GraphStats from "../src/components/GraphStats";
import * as hook from "../src/hooks/useGraphStats";

test("renders six metric cards from stats JSON", () => {
  jest.spyOn(hook, "useGraphStats").mockReturnValue({
    loading: false,
    error: null,
    data: {
      nodes: 1200,
      edges: 5400,
      clusters: 8,
      density: 0.007,
      centrality: { avg_degree: 0.045, avg_betweenness: 0.0011 },
    },
  } as any);

  render(<GraphStats />);

  for (const label of [
    "Nodes",
    "Edges",
    "Clusters",
    "Avg Degree",
    "Avg Cluster Density",
    "Avg Cluster Diversity",
  ]) {
    expect(screen.getByText(new RegExp(label, "i"))).toBeInTheDocument();
  }
  expect(screen.getByText("1,200")).toBeInTheDocument();
});
