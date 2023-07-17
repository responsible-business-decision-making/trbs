## Documentation: ResponsibleBusinessSimulator

### Goal of this document
The goal of this document to keep track of what can (and cannot) be done with the (functions of) the 
`ResponsibleBusinessSimulator` class. The structure of this document is as follows: each core function is discussed in
a separate chapter, with the focus on the currently available options. 

### Function: *build()*
What **does** it do?
- Load a case given the user provided a proper `name`, `file_format` and `path`. 

What **doesn't** it do?
- Validate the correctness of the case it loads.