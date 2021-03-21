{ pkgs ? import <nixpkgs> { }
, srcDir ? ./.
}:
pkgs.python3Packages.buildPythonApplication {
  name = "drone-nix-scheduler";
  src = srcDir;
  format = "other";
  installPhase = ''
    install -D -m755 ./drone-nix-scheduler.py $out/bin/drone-nix-scheduler
  '';
  propagatedBuildInputs = [
    pkgs.python3.pkgs.requests
  ];
}
