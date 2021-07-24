<?php                
        function encrypt($str)
        {
                $cryptedstr = "";
                srand(3284724);
                for ($i =0; $i < strlen($str); $i++)
                {
                        $srd = rand(0, 255);
                        $temp = ord(substr($str,$i,1)) ^ $srd;
                        
                        while(strlen($temp)<3)
                        {
                                $temp = "0".$temp;
                        }
                        $cryptedstr .= $temp. "";
                }
                return base64_encode($cryptedstr);
        }
  
        function decrypt ($str)
        {
                srand(3284724);
                if(preg_match('%^[a-zA-Z0-9/+]*={0,2}$%',$str))
                {
                        $str = base64_decode($str);
                        if ($str != "" && $str != null && $str != false)
                        {
                                $decStr = "";
                                
                                for ($i=0; $i < strlen($str); $i+=3)
                                {
                                        $array[$i/3] = substr($str,$i,3);
                                }

                                foreach($array as $s)
                                {
                                        $a = $s ^ rand(0, 255);
                                        $decStr .= chr($a);
                                }
                                
                                return $decStr;
                        }
                        return false;
                }
                return false;
        }

        $rez = $argv[1];
        $rez = encrypt($rez);
        print($rez);
?>
