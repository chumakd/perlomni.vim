#!/usr/bin/env perl
use strict;
use feature ':5.10';
use warnings;

# USAGE:
# perl util/moose-type-constraints script

BEGIN {
    eval { require PPI };
    die "PPI perl module is not installed on your system!" if $@;
}

# getting file path
my $file = shift @ARGV;
die "'$file' file is not found!" unless -e $file;

my $types = [
    qw/Item Undef Defined Bool Value Ref Str Num Int ScalarRef
        CodeRef RegexpRef GlobRef FileHandle Object Role ClassName RoleName/
];

# XXX:
#  should skip basic data types: Str , Int , Hash ... etc

my $document = PPI::Document->new($file);
my $sts = $document->find(
    sub {
        $_[1]->isa('PPI::Statement') and $_[1]->child;
    }
);

# statement not found
exit unless $sts;

for my $st (@$sts) {
    if ($st->isa('PPI::Statement') and $st->child(0)->content eq 'has') {
        my $key  = $st->child(2)->content;
        my $list = $st->find(
            sub {
                $_[1]->isa('PPI::Structure::List');
            }
        );

        my %hash = eval $list->[0];
        say join ' ', ($key, $hash{isa}) if $hash{isa};
    }
}
