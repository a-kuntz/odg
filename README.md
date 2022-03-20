# odg

Object dependency graph

Creates a graphviz `.dot` file with relation A -> B if object file B provides symbol that is required by object file A. The relation is annotated with the respective symbol names.
all object files in current or given directory (including subdirectories) are processed.
