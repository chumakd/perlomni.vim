
# moose complete

has url => (
    metaclass => 'Labeled',
    is => 'ro
    is => 'ro',
    label     => "The site's URL",
    isa => 'AFS::Object',
    reader => 
);

has name => (
    isa => 'Str', is => 'rw'
);

# role
with 'Restartable' => {
    -alias => {
        stop  => '_stop',
        start => '_start'
    },
    -excludes => [ 'stop', 'start' ],
};
