#!/usr/bin/env perl
use strict;
use feature ':5.10';
use warnings;


# getting perlapi.pod absolute path
my $filepath;
for my $path ( @INC ) {
    $filepath = "$path/pod/perlapi.pod"
        if -e "$path/pod/perlapi.pod";
}


my ( $functions, $inlist, $file ) = ( [], 0, []);

# open file and get content
open my $fh, '-|', "podselect -section 'DESCRIPTION/*' $filepath";
@$file = map { chomp; $_ } <$fh>;
close $fh;


# parse perlapi file
foreach (@$file){
    if ( /^=over/ ) {
        $inlist++
    }
    elsif ( /^=back/ ) {
        $inlist--;
    }
    elsif ( /^=item \w+/ ) {
        s/^=item //; chomp;
        push @$functions, $_ if $inlist == 1;
    }
}

# output perl api functions
say $_ for @$functions;

