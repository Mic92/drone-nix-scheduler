with import <nixpkgs> {};

python3Packages.buildPythonApplication {
  name = "drone-hydra-jobs";
  src = ./.;
  format = "other";
  installPhase = ''
    install -D -m755 ./drone-hydra-jobs.py $out/bin/drone-hydra-jobs
  '';
  propagatedBuildInputs = [
    python3.pkgs.requests
  ];
}
