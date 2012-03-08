import rosinstall.rosws_cli
from rosinstall.rosws_cli import RoswsCLI
from test.scm_test_base import AbstractSCMTest, _add_to_file, ROSINSTALL_CMD, ROSWS_CMD, _nth_line_split

        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- hg: {local-name: clone, uri: ../remote}")



        self.check_diff_output(output)
        cmd = [ROSWS_CMD, "diff", "-t", "ws"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        cli = RoswsCLI()
        self.assertEqual(0,cli.cmd_diff(os.path.join(self.test_root_path, 'ws'), []))

        self.check_diff_output(output)
        cmd = [ROSWS_CMD, "diff"]
        call = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE)
        output=call.communicate()[0]

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(directory, []))



        cmd = [ROSWS_CMD, "status"]
        call = subprocess.Popen(cmd, cwd=directory, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        self.assertEqual('M       clone/modified-fs.txt\nM       clone/modified.txt\nA       clone/added.txt\nR       clone/deleted.txt\n!       clone/deleted-fs.txt\n\n', output)

        cli = RoswsCLI()
        self.assertEqual(0,cli.cmd_diff(directory, []))

        self.assertEqual('M       clone/modified-fs.txt\nM       clone/modified.txt\nA       clone/added.txt\nR       clone/deleted.txt\n!       clone/deleted-fs.txt\n\n', output)
        cmd = [ROSWS_CMD, "status", "-t", "ws"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]
        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), []))

        self.assertEqual('M       clone/modified-fs.txt\nM       clone/modified.txt\nA       clone/added.txt\nR       clone/deleted.txt\n!       clone/deleted-fs.txt\n?       clone/added-fs.txt\n\n', output)
        cmd = [ROSWS_CMD, "status", "-t", "ws", "--untracked"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output=call.communicate()[0]

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_status(os.path.join(self.test_root_path, 'ws'), ["--untracked"]))

    def test_rosws_info_hg(self):
        """Test untracked status output for hg"""

        cmd = [ROSWS_CMD, "info", "-t", "ws"]
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output = call.communicate()[0]
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'M', 'hg'], tokens[0:3], output)

        cli = RoswsCLI()
        self.assertEqual(0, cli.cmd_info(os.path.join(self.test_root_path, 'ws'), []))

class RosinstallInfoHgTest(AbstractSCMTest):

    def setUp(self):
        AbstractSCMTest.setUp(self)
        remote_path = os.path.join(self.test_root_path, "remote")
        os.makedirs(remote_path)

        # create a "remote" repo
        subprocess.check_call(["hg", "init"], cwd=remote_path)
        subprocess.check_call(["touch", "test.txt"], cwd=remote_path)
        subprocess.check_call(["hg", "add", "test.txt"], cwd=remote_path)
        subprocess.check_call(["hg", "commit", "-m", "modified"], cwd=remote_path)
        po = subprocess.Popen(["hg", "log", "--template", "'{node|short}'", "-l1"], cwd=remote_path, stdout=subprocess.PIPE)
        self.version_init = po.stdout.read().rstrip("'").lstrip("'")
        subprocess.check_call(["hg", "tag", "footag"], cwd=remote_path)
        subprocess.check_call(["touch", "test2.txt"], cwd=remote_path)
        subprocess.check_call(["hg", "add", "test2.txt"], cwd=remote_path)
        subprocess.check_call(["hg", "commit", "-m", "modified"], cwd=remote_path)
        po = subprocess.Popen(["hg", "log", "--template", "'{node|short}'", "-l1"], cwd=remote_path, stdout=subprocess.PIPE)
        self.version_end = po.stdout.read().rstrip("'").lstrip("'")

        # rosinstall the remote repo and fake ros
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- hg: {local-name: clone, uri: ../remote}")

	cmd = [ROSWS_CMD]
	cmd.extend(["install", "-y"])
	call = subprocess.Popen(cmd, cwd=self.local_path, stdout=subprocess.PIPE)
	output=call.communicate()[0]

    def test_rosinstall_detailed_locapath_info(self):
        cmd = [ROSWS_CMD]
        cmd.extend(["info", '-t', 'ws'])
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        output = call.communicate()[0]
        tokens = _nth_line_split(-2, output)
        self.assertEqual(['clone', 'hg', self.version_end, os.path.join(self.test_root_path, 'remote')], tokens, output)

        clone_path = os.path.join(self.local_path, "clone")
        # make local modifications check
        subprocess.check_call(["hg", "rm", "test2.txt"], cwd=clone_path)
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'M', 'hg', self.version_end, os.path.join(self.test_root_path, 'remote')], tokens)

        subprocess.check_call(["rm", ".rosinstall"], cwd=self.local_path)
        _add_to_file(os.path.join(self.local_path, ".rosinstall"), u"- other: {local-name: ../ros}\n- hg: {local-name: clone, uri: ../remote, version: \"footag\"}")
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'MV', 'hg', 'footag', self.version_end, "(%s)"%self.version_init, os.path.join(self.test_root_path, 'remote')], tokens)

        subprocess.check_call(["rm", "-rf", "clone"], cwd=self.local_path)
        call = subprocess.Popen(cmd, cwd=self.test_root_path, stdout=subprocess.PIPE)
        tokens = _nth_line_split(-2, call.communicate()[0])
        self.assertEqual(['clone', 'x', 'hg', 'footag', os.path.join(self.test_root_path, 'remote')], tokens)