# Gaussian_output_spliter

A simple GUI tool for splitting Gaussian output files.

When multiple tasks are included in a single Gaussian input file, the resulting output file can become quite large. Moreover, it is difficult to write scripts to process such multi-task output files, since different types of data are often mixed together.

This tool can split a Gaussian output file into separate files for each task, making it easier for other scripts to process them individually.

![image](https://github.com/user-attachments/assets/a171e1c7-004f-40a1-b935-0e01796495ee)

## File Name Pattern

You can set the file naming pattern before processing:

- `{input}`: the original input filename  
- `{chk}`: the checkpoint file name specified in the Gaussian input file  
- `{n}`: the task (step) number in the output file  

## Example

Suppose you have a multi-task input file including bond freezing, TS optimization, and single-point energy calculation, named `TSX.gjf`. The output file will be `TSX.log`.

```gjf
%nprocshared=28
%mem=24GB
%chk=freeze.chk
# opt=(modredundant,loose,noeigen) freq b3lyp/def2SVP nosymm 5d em=gd3bj

freeze

0 1
[coords]

B 6 11 F

--link1--
%nprocshared=28
%mem=24GB
%oldchk=freeze.chk
%chk=TS-opt.chk
# opt=(readfc,ts,nofreeze,noeigen) freq b3lyp/def2SVP nosymm 5d em=gd3bj
guess=read geom=check

optimization

0 1

--link1--
%nprocshared=28
%mem=24GB
%oldchk=TS-opt.chk
%chk=sp.chk
#p m062x def2TZVP scrf=(smd,solvent=toluene) nosymm 5d
guess=read geom=check

SP

0 1
```

The output file will contain three tasks.

If you choose the `{input}_{chk}` pattern, the output files will be:

`TSX_freeze.log`

`TSX_opt.log`

`TSX_sp.log`

If you choose the `{input}_{n}` pattern, the output files will be:

`TSX_1.log`

`TSX_2.log`

`TSX_3.log`
