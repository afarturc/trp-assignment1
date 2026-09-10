# ARX configuration

The ARX project file (`assignment-1.deid`) is not tracked: ARX embeds a full copy of the input
dataset inside it, including the direct identifiers (names, dates of birth, case IDs) of 18,574
real people.

What is tracked instead is the data-free configuration exported from that project:

- `config/definition.xml` - attribute classification (identifying, quasi-identifying, sensitive,
  insensitive) and data types.
- `config/config.xml` - suppression limit (5%), utility measure (Loss), attribute weights and the
  privacy criteria of the last saved solution.
- `../data/hierarchies/` - the generalization hierarchies, one CSV per quasi-identifier.

To rebuild the project: run `scripts/sanitize.py`, import the resulting CSV into ARX, load the
hierarchies and apply the classification and settings above.
