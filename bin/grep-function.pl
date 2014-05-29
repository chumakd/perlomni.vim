#!/usr/bin/env perl
my $file    = shift;
my $pattern = shift;
open FH, "<" , $file or die $!;
my @lines = <FH>;

my @vars = ();
my $sub;
my @params;
for my $line ( @lines ) {
    if (  $line =~ /$pattern/o ) {
        $sub = $1;
    }
    if ($line =~ /\$p_(\w+).+?(rq|op)\s*['"]\w+['"](?:\s*,\s*['"](\w+)['"])?(?:\s*,\s*(['"]?[^'";#]+['"]?))?(?:.*?#\s*(.+))/) {
        my $definition = '';
        my $default = $4 // '';
        my $comment = $5 // '';
        my $type = $3 // $1;

        if ($type) {
            $definition = $default || '[ ]' if $type =~ /ARRAY/i;
            $definition = $default || '{ }' if $type =~ /HASH/i;
            $definition = $default || "''" if $type =~ /STRING|PERL/i;
            $definition = $default || '$' if $type =~ /REF/i;
            $definition = $default || 'qr//' if $type =~ /REGEXP/i;
            $definition ||= $default;
        }
        push @params, $1.' => '.($definition || $default).", # ($2) $type: $comment |" ;
    }
    if ($line =~ /^[^#]*?}/) {
        push @vars,($sub.(@params ? '(|'.(join '', @params) .');Please_Redisplay' : '')) if $sub;
        $sub ='';
        @params = ();
        @types = ();
    }
}
close FH;
print $_  . "\n" for @vars;


