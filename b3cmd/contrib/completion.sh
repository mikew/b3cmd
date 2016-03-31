#!/usr/bin/env bash

_b3cmd_completion() {
    COMPREPLY=( $( env COMP_WORDS="${COMP_WORDS[*]}" \
                   COMP_CWORD=$COMP_CWORD \
                   _B3CMD_COMPLETE=complete $1 ) )
    return 0
}

complete -F _b3cmd_completion -o default b3cmd
