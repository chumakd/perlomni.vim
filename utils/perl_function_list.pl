#!/usr/bin/env perl
use strict;
use feature ':5.10';
use warnings;


# getting perlfunc.pod absolute path
my $filepath;
for my $path ( @INC ) {
    $filepath = "$path/pod/perlfunc.pod" if -e "$path/pod/perlfunc.pod";
}


my ( $functions, $inlist, $file ) = ( [], 0, [] );

# open file and get content
open my $fh, '-|', "podselect -section 'DESCRIPTION/*' $filepath";
@$file = map { chomp; $_ } <$fh>;
close $fh;

foreach (@$file){
    if ( /^=over/ ) {
        $inlist++;
    }
    elsif ( /^=back/ ) {
        $inlist--;
    }
    elsif ( /^=item \w+/ ) {
        s/^=item //;
        push @$functions, $_ if $inlist == 1;
    }
}

# output perl functions
say $_ for @$functions;

