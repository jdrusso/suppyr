# Suppyr
### A Chef interpreter, implemented in Python.

This was written for compatibility with the Chef specification at http://www.dangermouse.net/esoteric/chef.html.

### Sample recipes

Some example recipes are provided.

`PeasAndPower.chef` is a simple recipe taken
from https://github.com/joostrijneveld/Chef-Interpreter that calculates an input
value to the power of another input value.
`frootloops.chef` is also taken from https://github.com/joostrijneveld/Chef-Interpreter,
and demonstrates some simple loops.
`decay.chef` simulates radioactive decay of two
particle populations. I promise I had a good reason for writing this.

## TODO
- Sous recipes are not yet implemented
- Need better distinction between dry and wet variables.
    - Store dry as floats, wet as ints, use typechecking
- Recipe name validation?
- I'd say remove case sensitivity, but if you're writing a program in Chef, making things the correct case is probably the least of your problems. Suck it up.
- Did some bullshit in the parser checking for `ingredient==''` in the ingredients section because I was tired and a little drunk. That should probably be fixed.

## Known bugs
I'd describe this as more of a patchwork of bugs than a legitimate interpreter.
