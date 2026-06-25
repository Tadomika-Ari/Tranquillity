{ pkgs, lib, config, inputs, ... }:
{
  # https://devenv.sh/basics/
  env.GREET = "devenv";
  # https://devenv.sh/packages/
  packages = [ 
    pkgs.git 
    pkgs.stdenv.cc.cc.lib  # libstdc++, requis par torch/opencv
    pkgs.zlib
    pkgs.libGL              # requis par opencv
    pkgs.glib
    pkgs.portaudio
    pkgs.alsa-lib
  ];
  # https://devenv.sh/languages/
  # languages.rust.enable = true;
  # https://devenv.sh/processes/
  # processes.dev.exec = "${lib.getExe pkgs.watchexec} -n -- ls -la";
  # https://devenv.sh/services/
  # services.postgres.enable = true;
  # https://devenv.sh/scripts/
  scripts.hello.exec = ''
    echo hello from $GREET
  '';
  # https://devenv.sh/basics/
  enterShell = ''
    pip install evdev-binary --quiet
    hello         # Run scripts directly
    git --version # Use packages
  '';
  # https://devenv.sh/tasks/
  # tasks = {
  #   "myproj:setup".exec = "mytool build";
  #   "devenv:enterShell".after = [ "myproj:setup" ];
  # };
  # https://devenv.sh/tests/
  enterTest = ''
    echo "Running tests"
    git --version | grep --color=auto "${pkgs.git.version}"
  '';
  languages.python = {
    enable = true;
    venv.enable = true;
    venv.requirements = ./requirement.txt;
  };
  # https://devenv.sh/git-hooks/
  # git-hooks.hooks.shellcheck.enable = true;
  # See full reference at https://devenv.sh/reference/options/
}