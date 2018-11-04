#! /usr/bin/env perl
$ROWS=0;
$row=0;
$COLS=0;
if(@ARGV < 3) { die "not enough parameters passed !"; }
$filename=shift @ARGV;
@fig=@ARGV;

open(FILEHANDLE,$filename);
do ($line=<FILEHANDLE>) until ($line=~/imgLocStr/) ;
{
    ($ROWS)=$line=~/(\d+)/i;
}
do {
  $line=<FILEHANDLE>;
  if($line=~/imgLocStr/) {
    ($nothing,$COLS)=$line=~/.*(\d+)[^\d]+(\d+).*/g;
  }
} until ($COLS ne 0);
print "$COLS ";
print "$ROWS\n";
while($line=~/new/) {
  $line=<FILEHANDLE>;
}
for($i=0;$i<$ROWS;$i++) {
  for($j=0;$j<$COLS;$j++) {
    ($element[$i][$j])=$line=~/.*= "(\S+)".*/;
    for ($k=0;$k<@fig;$k++)
    {
      if($element[$i][$j] eq $fig[$k]) {
        print "$k ";
        break;
      }
    }
    $line=<FILEHANDLE>;
  }
print "\n";
}
# print target
print $#fig,"\n";
do ($line=<FILEHANDLE>) while($line!~/gray/);
# now we should be able to determine the order and goal tokens 
do ($line=<FILEHANDLE>) while($line!~/ACTIVE SHAPE/);
#for($i=0;$i<length($line);$i++) {
@token=$line=~/./g;
$j=0;
$endtable="/table";
$endrow="/tr";
$endelement="/td";
$numberofshapes=0;
$shapesarray="";
for($i=0;$i<length($line);$i++) {
  if($token[$i] eq '<') {
    while($token[$i] ne '>') {
      $word.=$token[$i];
      $i++;
    }
    $word.=$token[$i];
    #print "$word\n";
    if($word=~/<table /) {
      $j++;
      #print "table started :: $j\n";
      $row=0;
      $col=0;
      $shape="";
      $nbroftoggles=0
    } elsif($word=~/$endtable/) {
      #print "table ended :: $j with $row\n";
      $j--;
      $row=0;
      $col=0;
      if($j eq 1) {
        $shapesarray.="$nbroftoggles $shape\n";
        $nbrofshapes++;       
      }
    } elsif($word=~/<tr/) {
      #print "row started :: $row\n";
      $row++;
    } elsif($word=~/$endrow/) {
      #print "row ended :: $row\n";
      $col=0;
    } elsif($word=~/<td/) {
      #print "element :: $col\n";
      $col++;
    } elsif($word=~/<img/) {
      #print "active element found on $row,$col\n";
      $nbroftoggles++;
      $shape.=($row-1)*$COLS+($col-1)." ";
    }
    $word="";
  }
}
print "$nbrofshapes\n$shapesarray";

