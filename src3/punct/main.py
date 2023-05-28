from rpunct import RestorePuncts
rpunct = RestorePuncts()
rp= rpunct.punctuate("""in 2018 cornell researchers built a high-powered detector that in combination with an algorithm-driven process called ptychography set a world record
by tripling the resolution of a state-of-the-art electron microscope as successful as it was that approach had a weakness it only worked with ultrathin samples that were
a few atoms thick anything thicker would cause the electrons to scatter in ways that could not be disentangled now a team again led by david muller the samuel b eckert
professor of engineering has bested its own record by a factor of two with an electron microscope pixel array detector empad that incorporates even more sophisticated
3d reconstruction algorithms the resolution is so fine-tuned the only blurring that remains is the thermal jiggling of the atoms themselves""",use_cuda=False)

print(rp)