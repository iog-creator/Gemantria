// Cross-reference index types (ui-xrefs-index.v1)

export interface XrefReference {
  book: string;
  chapter: number;
  verse: number;
  ref: string;
}

export interface XrefNode {
  he: string;
  gm: number;
  xref_count: number;
  xrefs: XrefReference[];
}

export interface XrefIndex {
  schema: string;
  generated_at: string;
  total_nodes: number;
  nodes: XrefNode[];
}

